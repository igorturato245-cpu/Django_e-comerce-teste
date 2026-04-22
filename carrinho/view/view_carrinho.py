from django.shortcuts import render,redirect
from carrinho.models import ItemCarrinho,Carrinho
from e_comerce.services import erp as erp_service
from decimal import Decimal,ROUND_HALF_UP

def _get_cart_for_request(request):
    if request.user.is_authenticated:
        cart,_=Carrinho.objects.get_or_create(usuario=request.user)
        return cart
    
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key=request.session.session_key
    cart,_=Carrinho.objects.get_or_create(
        session_key=session_key
    )
    
    return cart


def carrinho(request):
    carrinho=_get_cart_for_request(request)

    if not carrinho:
        itens=[]
        subtotal=0
    else:
        itens=carrinho.itens.select_related('produto').all() # type: ignore
                    
        subtotal=carrinho.total()
            
    context = {
        'is_index': False,
        'Items':itens,
        'subtotal':subtotal,
    }
    return render(request, 'carrinho/carrinho.html', context)