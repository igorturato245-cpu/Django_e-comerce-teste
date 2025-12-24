from django.shortcuts import render
from carrinho.models import ItemCarrinho,Carrinho

def _get_cart_for_request(request):
    if request.user.is_authenticated:
        try:
            return Carrinho.objects.get(usuario=request.user)
        except Carrinho.DoesNotExist:
            return None
        
    session_key = request.session.session_key
    if not session_key:
        return None
    try:
        return Carrinho.objects.get(session_key=session_key)
    except Carrinho.DoesNotExist:
        return None


def carrinho(request):
    carrinho=_get_cart_for_request(request)

    if not carrinho:
        itens=[]
        subtotal=0
    else:
        itens=carrinho.itens.select_related('produto').all() # type: ignore
        subtotal = sum(
        item.produto.preco * item.quantidade
        for item in itens
        )
    
    context = {
        'is_index': False,
        'Items':itens,
        'subtotal':subtotal,
    }
    return render(request, 'carrinho/carrinho.html', context)
