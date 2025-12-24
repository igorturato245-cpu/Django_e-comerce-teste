from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from carrinho.models import Carrinho, ItemCarrinho
from e_comerce.models import Produto

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

    if hasattr(produto,'estoque') and produto.estoque is not None:
        if produto.estoque <=0:
            messages.error(request,'Produto sem estoque') # type: ignore
            return redirect('Produtos:index')
        if quantidade > produto.estoque:
            quantidade = produto.estoque
    
    item, created=ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'quantidade':quantidade},
    )

    if not created:
        item.quantidade=max(1,item.quantidade)
        item.save()

    acao =request.POST.get('acao')

    if acao == 'comprar':
        return redirect('carrinho:carrinho')
    return redirect('produtos:index')