import logging
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from carrinho.view.view_carrinho import _get_cart_for_request,carrinho
from pagamentos.models import Pedido, PedidoItem, Solicitacao_reembolso
from pagamentos.integrations import pagseguro as pagseguro_integration
from pagamentos.tasks import send_order_to_erp_task,send_order_cancelled_to_erp_task
from decimal import Decimal,ROUND_HALF_UP
from cadastro_de_usuarios.models import Endereco
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from e_comerce.models import Produto,Avaliacao_produto
from pagamentos.utils import require_api_erp,require_api_payment
from django.conf import settings

logger = logging.getLogger(__name__)

@require_api_payment
def start_payment(request):
    if not request.user.is_authenticated:
        return redirect ('cadastro_login:loginuser')
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido')
        return redirect('carrinho:carrinho')

    cart = _get_cart_for_request(request)
    if not cart or not cart.itens.exists():
        messages.error(request, 'Carrinho vazio')
        return redirect('carrinho:carrinho')

    items = cart.itens.select_related('produto').all()
    
    #for i in items:
    #    preco=i.produto.preco_promocional or i.produto.preco
    #    subtotal=preco * i.quantidade
    
    total = cart.total()
    
    pedido_existente=Pedido.objects.filter(
        usuario=request.user,
        carrinho=cart
    ).exists()
    
    if pedido_existente:
        messages.error(request,'Pedido ja existe e está em processo, aguarde.')
        return redirect('carrinho:carrinho')
    
    endereco=get_object_or_404(Endereco,usuario=request.user,padrao=True)
    
    itens_para_calculo=[]
    for item in items:
        itens_para_calculo.append({
            'id':item.produto.erp_id or str(item.produto.id),
            'quantity':item.quantidade
        })
    
    total_com_frete=Pedido.calcula_total(cep=endereco.cep,itens=itens_para_calculo,total=total)
    
    try:    
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                carrinho=cart,
                valor_frete=total_com_frete['valor_frete'],
                total=total_com_frete['total'],
                total_com_frete=total_com_frete['total_com_frete'],
                status='pending'
            )
            for it in items:
                PedidoItem.objects.create(
                    pedido=pedido,
                    produto=it.produto,
                    produto_id_string=str(it.produto.erp_id or it.produto.id),
                    produto_name=it.produto.name,
                    quantidade=it.quantidade,
                    price=it.produto.get_preco()
                )
                
                
    except ImportError:
        messages.error(request,'Pedido ja esta sendo processado, aguarde.')
        return redirect('carrinho:carrinho')
    
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
        return redirect('pagamentos:meus_pedidos')
    
    
@login_required
@require_POST   
@require_api_payment
def retry_payment(request,pedido_id):   
    
    try:
        with transaction.atomic():
            pedido=get_object_or_404(Pedido.objects.select_for_update(),pk=pedido_id,usuario=request.user)
            
            if pedido.status != 'pending':
                messages.error(request,'Erro ao processar pedido, status atual não permite retry.')
                return redirect('pagamentos:meus_pedidos')
    except ImportError:
        messages.error(request,'Error ao acessar o pedido.Tente novamente.')
        return redirect('pagamentos:meus_pedidos')
    
    try:
        
        return_url=request.build_absolute_uri(reverse('pagamentos:payment_return'))
        notification_url=request.build_absolute_uri(reverse('pagamentos:pagseguro_notify'))
        
        pg_data=pagseguro_integration.create_checkout(pedido,return_url,notification_url)
        
        pedido.payment_reference=pg_data['reference']
        pedido.metadata={'pagseguro_code':pg_data['code']}
        pedido.save(update_fields=['payment_reference','metadata'])
        
        return redirect(pg_data['return_url'])
    
    except Exception as e:
        logger.error(f"Erro ao criar retentativa de pagamento para o pedido {pedido_id}: {e}")
        messages.error(request, 'Erro de comunicação com o gateway de pagamento. Tente novamente mais tarde.')
        return redirect('pagamentos:detalhe_pedido', pedido_id=pedido.pk)

 
 
    

@require_POST   
@login_required
@require_api_payment
def cancelled_refunded_return(request,pedido_id):
    
    pedido=get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    pode_cancelar = pedido.status in ['paid','erp_sent','erp_confirmed'] and pedido.erp_status in ['paid','confirmed']
    
    if pode_cancelar:
        try:
            with transaction.atomic():                    
                if pedido.status == 'paid':
                    transaction_code=(pedido.metadata or {}).get('pagseguro_code')
                    if not transaction_code:
                        raise Exception('Código de transação do PagSeguro não encontrado no pedido')
                    
                pg=pagseguro_integration.refund_transaction(transaction_code)
                    
                if not pg:
                    raise Exception('Falha ao processar reembolso no PagSeguro')
                
                pedido.status ='cancelled'
                pedido.save()
                
                send_order_cancelled_to_erp_task.delay(pedido.id) #type:ignore
                
                messages.success(request,'Pedido cancelado com sucesso.')
            
        except Exception as e:
            messages.error(request,f'Erro ao cancelar pedido: {str(e)}')
            
    else:
        messages.error(request,'Pedido não pode ser cancelado, status atual: {pedido.status}')
        
    return redirect('pagamentos:meus_pedidos')


    
    
@require_api_payment
def payment_return(request):
    reference = request.GET.get('reference')
    status = request.GET.get('status', 'pending')
    context = {
        'reference': reference,
        'status': status,
        'success': status in ['3', 'paid']
    }
    return render(request, 'pagamentos/return.html', context)

@require_api_payment
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
        status_code = str(data.get('status'))
        
        # Início da Transação Atômica
        with transaction.atomic():
            # select_for_update(): Trava a linha no BD até o fim da transação
            pedido = Pedido.objects.select_for_update().filter(payment_reference=ref).select_related('carrinho','usuario').first()
            
            if not pedido:
                logger.error(f"Pedido não encontrado para reference: {ref}")
                return HttpResponse(status=404)
            
            if pedido.status == 'paid':
                return HttpResponse('Ok')
            
            status_map = {
                '1': 'pending', '2': 'pending', '3': 'paid',
                '4': 'paid',    '5': 'cancelled', '6': 'refunded',
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
                
                logger.info(f"Pedido {pedido.pk} atualizado para status: {new_status}")
                
                if new_status == 'paid':
                    with transaction.atomic():
                    # on_commit: Só dispara a task se o DB confirmar a gravação do 'paid'
                        transaction.on_commit(lambda: send_order_to_erp_task.delay(pedido.pk))
                    
        return HttpResponse('OK')
        
    except Exception as e:
        logger.error(f"Erro ao processar notificação: {e}")
        return HttpResponse(status=500)
    
@require_api_erp 
@require_api_payment  
def checkout(request):
    
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    endereco=Endereco.objects.filter(usuario=request.user,padrao=True).first()  or \
                   Endereco.objects.filter(usuario=request.user).first()
    
    cart=_get_cart_for_request(request)
    
    if not cart or not cart.itens.exists():
        messages.error(request,'Carrinho vazio.')
        return redirect('pagamentos:meus_pedidos')
    
    if not endereco:
        messages.error(request,'Necessario endereço para concluir a compra')
        return redirect('cadastro_login:criarend')
    
    itens=cart.itens.select_related('produto').all()
    
    itens_para_frete=[]
    
    from e_comerce.services import erp as erp_service
    
    for item in itens:
        itens_para_frete.append({
            'id':item.produto.erp_id or str(item.produto.id),
            'quantity':item.quantidade
        })
        
        if item.produto.erp_id:
            try:
                # Consulta o fornecedor uma última vez
                avail = erp_service.check_availability(item.produto.erp_id, item.quantidade)
                
                if not avail['available']:
                    # Se o estoque mudou, atualizamos o carrinho dele na hora
                    nova_qtd = avail['stock']
                    item.quantidade = nova_qtd
                    item.save()
                    
                    if nova_qtd == 0:
                        item.delete()
                        messages.warning(request, f"O produto {item.produto.name} esgotou e foi removido.")
                    else:
                        messages.warning(request, f"A quantidade de {item.produto.name} foi ajustada para {nova_qtd} (limite do estoque).")
                    
                    # Se algo mudou, mandamos ele de volta para o carrinho para revisar
                    return redirect('carrinho:carrinho')
            except Exception as e:
                # Se a API do fornecedor cair, por segurança, você decide:
                # Aqui vamos deixar passar com log, mas você poderia travar.
                logger.error(f"Erro ao validar estoque no checkout: {e}")
             
    calcular_frete=Pedido.calcula_total(cep=endereco.cep,itens=itens_para_frete,total=cart.total())
    
    request.session['frete_calculado']=str(calcular_frete['valor_frete'])
    
    context={
        'itens':itens,
        'valor_frete':calcular_frete['valor_frete'],
        'prazo':calcular_frete['prazo_entrega'],
        'subtotal':calcular_frete['total'],
        'total_com_frete':calcular_frete['total_com_frete'],
        'endereco':[endereco],
        'cart':cart,
    }
    
    return render(request,'pagamentos/checkout.html',context)

def meuspedidos(request):
    
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    
    pedido=Pedido.objects.filter(usuario=request.user).order_by('-created_at')
    
    context={
        'pedidos':pedido,
    }
    
    return render(request,'pagamentos/meus_pedidos.html', context)


def detalhepedido(request,pedido_id):
    
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    pedido=get_object_or_404(Pedido,pk=pedido_id, usuario=request.user)
    
    itens=PedidoItem.objects.filter(pedido=pedido)
    
    context={
        'pedido':pedido,
        'itens':itens,
    }
    
    return render(request,'pagamentos/detalhe_pedido.html',context)


def avaliar_pedido(request,pedido_id):
    
    if not request.user.is_authenticated:
        return redirect('cadastro:loginuser')
    
    pedido=get_object_or_404(Pedido,pk=pedido_id, usuario=request.user)
    
    if request.method == 'POST':
        nota_site=request.POST.get('rating_site')
        nota_produto=request.POST.get('rating_prod')
        descricao=request.POST.get('feedback')
        
        itens_comprados=PedidoItem.objects.filter(pedido=pedido)
        
        if not itens_comprados.exists():
            messages.error(request, 'Este pedido não possui produtos para avaliar.')
            return redirect('produtos:index')
        
        
        for item in itens_comprados:
            
            Avaliacao_produto.objects.create(
                usuario=request.user,
                pedido=pedido,
                produto=item.produto,
                nota_site=int(nota_site) if nota_site else 5,
                nota_produto=int(nota_produto) if nota_produto else 5,
                comentario=descricao,
            )
            
        messages.success(request,'Sucesso ao avaliar o produto.')
        return redirect('produtos:index')
    
    return render(request,'pagamentos/avaliar_pedido.html',{'pedido':pedido})   

@require_api_erp 
def cancelar_reembolsar_pedido(request,pedido_id):
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
     
    pedido=get_object_or_404(Pedido,id=pedido_id,usuario=request.user)
    
    itens=PedidoItem.objects.filter(pedido=pedido)
    
    context={
        'pedido':pedido,
        'itens':itens,
    }
    
    
    return render(request,'pagamentos/cancelar_reembolsar.html', context)



@require_POST 
def solicitar_cancelamento(request,pedido_id):
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    pedido=get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    
    if request.method == 'POST':
        
        motivo=request.POST.get('motivo-devolucao')
        feedback=request.POST.get('feedback-devolucao')
        evidencias=request.FILES.get('evidencias-reembolso')
        
        Solicitacao_reembolso.objects.create(
            pedido=pedido,
            motivo=motivo,
            feedback=feedback,
            evidencias=evidencias,
            status='pending'
        )
        
        messages.success(request,'Solicitação de cancelamento/reembolso enviada com sucesso. Aguarde nosso contato.')
        return redirect('pagamentos:meus_pedidos')
    
    
def analise_reembolso(request,pedido_id):
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    
    pedido=get_object_or_404(Pedido,id=pedido_id, usuario=request.user)
    
    solicitacao=Solicitacao_reembolso.objects.filter(pedido=pedido).first()
    
    
    context={
        'pedido':pedido,
        'solicitacao':solicitacao,
    }
    
    return render(request, 'pagamentos/analise_reembolso.html',context)
    
    
    
    
    
@require_POST 
def reembolso_solicitacao_aprovada(request,pedido_id):
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    pedido=get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    status_solicitacao=Solicitacao_reembolso.objects.filter(pedido=pedido).first()
    
    if not status_solicitacao or status_solicitacao.status != 'approved':
        messages.error(request,'Solicitação de reembolso não aprovada ou inexistente.')
        return redirect('pagamentos:meus_pedidos')
    else:
        try:
            with transaction.atomic():
                if pedido.status in ['cancelled','refunde_requested'] and pedido.erp_status in ['cancelled']:
                    transaction_code=pedido.metadata.get('pagseguro_code')
                    
                    if not transaction_code:
                        raise Exception('Código de transação do PagSeguro não encontrado no pedido')
                    
                    pg=pagseguro_integration.refund_transaction(transaction_code,amount=pedido.total_com_frete)
                    
                    if not pg:
                        raise Exception('Falha ao processar reembolso no PagSeguro')
                    
                    pedido.status='refunded'
                    pedido.erp_status='return'
                    pedido.save(update_fields=['status','erp_status'])
                    
                    status_solicitacao.status='completed'
                    status_solicitacao.save(update_fields=['status'])
                    
                    messages.success(request,'Reembolso processado com sucessso.')
        except Exception as e:
            messages.error(request,f'Erro ao processar reembolso: {str(e)}')
            
    return redirect('pagamentos:meus_pedidos')


def conclusao_cancelamento(request,pedido_id):
    if not request.user.is_authenticated:
        return redirect('cadastro_login:loginuser')
    
    
    pedido=get_object_or_404(Pedido,id=pedido_id, usuario=request.user)
    
    
    context={
        'pedido':pedido,
    }
    
    return render(request, 'pagamentos/conclusao_cancelamento.html',context)