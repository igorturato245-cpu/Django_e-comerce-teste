import logging
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
from carrinho.view.view_carrinho import _get_cart_for_request
from pagamentos.models import Pedido, PedidoItem
from pagamentos.integrations import pagseguro as pagseguro_integration
from pagamentos.tasks import send_order_to_erp_task

logger = logging.getLogger(__name__)

# ... (função start_payment e payment_return permanecem iguais) ...
def start_payment(request):
    # O código anterior estava correto, mantendo omitido para brevidade
    cart = _get_cart_for_request(request)
    if not cart or not cart.itens.exists():
        messages.error(request, 'Carrinho vazio')
        return redirect('carrinho:carrinho')

    items = cart.itens.select_related('produto').all()
    total = sum(item.produto.preco * item.quantidade for item in items)
    
    with transaction.atomic():
        pedido = Pedido.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            carrinho=cart,
            total=total,
            status='pending'
        )
        for it in items:
            PedidoItem.objects.create(
                pedido=pedido,
                produto_id=str(it.produto.erp_id or it.produto.id),
                produto_name=it.produto.name,
                quantidade=it.quantidade,
                price=it.produto.preco
            )
    
    try:
        # Nota: Garante que settings.SECURE_PROXY_SSL_HEADER esteja configurado
        # em produção para gerar links HTTPS corretos
        return_url = request.build_absolute_uri(reverse('pagamentos:payment_return'))
        notification_url = request.build_absolute_uri(reverse('pagamentos:pagseguro_notify'))
        
        pg_data = pagseguro_integration.create_checkout(pedido, return_url, notification_url)
        
        pedido.payment_reference = pg_data['reference']
        pedido.metadata = {'pagseguro_code': pg_data['code']}
        pedido.save(update_fields=['payment_reference', 'metadata'])
        
        return redirect(pg_data['redirect_url'])
        
    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {e}")
        messages.error(request, 'Erro ao processar pagamento. Tente novamente.')
        return redirect('carrinho:carrinho')

def payment_return(request):
    reference = request.GET.get('reference')
    status = request.GET.get('status', 'pending')
    context = {
        'reference': reference,
        'status': status,
        'success': status in ['3', 'paid']
    }
    return render(request, 'pagamentos/return.html', context)

@csrf_exempt
def pagseguro_notification(request):
    """
    Webhook para notificações do PagSeguro com Proteção de Concorrência
    """
    notification_code = request.POST.get('notificationCode')
    if not notification_code:
        return HttpResponse(status=400)

    try:
        # 1. Valida a notificação na API do PagSeguro
        data = pagseguro_integration.get_notification_data(notification_code)
        
        if not data or not pagseguro_integration.validate_notification(data):
            logger.warning(f"Dados de notificação inválidos: {data}")
            return HttpResponse(status=400)
        
        ref = data.get('reference')
        status_code = data.get('status')
        
        # Início da Transação Atômica
        with transaction.atomic():
            # select_for_update(): Trava a linha no BD até o fim da transação
            pedido = Pedido.objects.select_for_update().filter(payment_reference=ref).first()
            
            if not pedido:
                logger.error(f"Pedido não encontrado para reference: {ref}")
                return HttpResponse(status=404)
            
            status_map = {
                '1': 'pending', '2': 'review', '3': 'paid',
                '4': 'paid',    '5': 'dispute', '6': 'refunded',
                '7': 'cancelled',
            }
            
            new_status = status_map.get(status_code, 'pending')
            
            # Só atualiza se houver mudança de status
            if pedido.status != new_status:
                pedido.status = new_status
                pedido.metadata = pedido.metadata or {}
                pedido.metadata.update({
                    'pagseguro_status': status_code,
                    'pagseguro_last_update': data.get('lastEventDate'),
                    'pagseguro_transaction_code': data.get('code'),
                })
                pedido.save(update_fields=['status', 'metadata'])
                
                logger.info(f"Pedido {pedido.id} atualizado para status: {new_status}")
                
                if new_status == 'paid':
                    # on_commit: Só dispara a task se o DB confirmar a gravação do 'paid'
                    transaction.on_commit(lambda: send_order_to_erp_task.delay(pedido.id))
        
        return HttpResponse('OK')
        
    except Exception as e:
        logger.error(f"Erro ao processar notificação: {e}")
        return HttpResponse(status=500)