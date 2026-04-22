import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from carrinho.models import Carrinho, ItemCarrinho
from e_comerce.models import Produto
from e_comerce.services import erp as erp_service
from carrinho.view.view_carrinho import _get_cart_for_request

logger=logging.getLogger(__name__)

def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = _get_cart_for_request(request)

    try:
        quantidade_adicionada = int(request.POST.get("quantidade", 1))
    except (TypeError, ValueError):
        quantidade_adicionada = 1

    # 1. Tenta buscar o item ou criar um novo
    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={
            'quantidade': 0, # Começa com 0 para somarmos corretamente abaixo
            'preco_unitario': produto.get_preco()
        }
    )

    # 2. Lógica de Soma: nova quantidade + o que já tinha lá
    quantidade_total = item.quantidade + quantidade_adicionada

    # 3. Verificação de estoque e fornecedor (Apenas na adição)
    if produto.erp_id:
        try:
            avail = erp_service.check_availability(produto.erp_id, quantidade_total)
            if not avail.get('available', False):
                # Se não tem o total, tentamos baixar para o que tem no estoque
                quantidade_total = avail.get('stock', 0)
                messages.warning(request, 'Quantidade ajustada para o limite do fornecedor.')
            
            # Atualizamos os dados do produto com o preço/estoque mais recente do ERP
            produto.remote_price = avail.get('price')
            produto.remote_stock = avail.get('stock')
            produto.estoque = avail.get('stock', 0)
            produto.save(update_fields=['remote_price', 'remote_stock', 'estoque'])
        except Exception as e:
            logger.warning(f"Erro ao checar ERP: {e}")

    # 4. Validação final no Model e SAVE único
    try:
        item.atualiza_qtd(quantidade_total)
        item.save()
        if created:
            messages.success(request, f'{produto.name} adicionado ao carrinho.')
    except Exception as e:
        messages.error(request, str(e))

    acao = request.POST.get('acao')
    if acao == 'comprar':
        return redirect('carrinho:carrinho')
    return redirect('produtos:index')