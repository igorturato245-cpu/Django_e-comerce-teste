import logging
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from carrinho.models import Carrinho, ItemCarrinho
from e_comerce.models import Produto
from e_comerce.services import erp as erp_service

logger=logging.getLogger(__name__)

def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart,created=Carrinho.objects.get_or_create(usuario=request.user)
        return cart
    
    session_key=request.session.session_key
    if not session_key:
        request.session.save()
        session_key=request.session.session_key
    cart,created=Carrinho.objects.get_or_create(session_key=session_key)
    return cart


def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = _get_or_create_cart(request)

    try:
        quantidade=int(request.POST.get("quantidade",1))
    except(TypeError,ValueError):
        quantidade=1

    quantidade=max(1,quantidade)

    erp_available=False
    if produto.erp_id:
        try:
            avail=erp_service.check_availability(produto.erp_id,quantidade)

            if not avail.get('available', False):
                messages.error(request,'Produto indisponível no fornecedor.') #type:ignore
                return redirect('produtos:index')
            

            produto.remote_price=avail.get('price')
            produto.remote_stock=avail.get('stock')
            produto.estoque=min(produto.estoque,avail.get('stock',0))
            produto.save(update_fields=['remote_price','remote_stock', 'estoque'])
            erp_available=True

        except Exception as e:
            logger.warning(f"ERP Indisponível ao adicionar carrinho (ID {produto.erp_id}): {e}")
            messages.warning(request, 'Não foi possível verificar estoque atualizado no fornecedor.') #type:ignore

    if hasattr(produto,'estoque') and produto.estoque is not None:
        if produto.estoque <=0:
            messages.error(request,'Produto sem estoque') # type: ignore
            return redirect('Produtos:index')
        if quantidade > produto.estoque:
            quantidade = produto.estoque
            messages.info(request, f'Quantidade ajustada para o estoque disponível: {quantidade}') #type:ignore
    
    item, created=ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'quantidade':quantidade},
    )

    if not created:
        item.quantidade=max(1,item.quantidade)
        if item.quantidade > produto.estoque:
            item.quantidade=produto.estoque
            messages.warning(request, f'Você já possui a quantidade máxima deste item no carrinho.') #type:ignore
        item.save()

    acao =request.POST.get('acao')

    if acao == 'comprar':
        return redirect('carrinho:carrinho')
    return redirect('produtos:index')