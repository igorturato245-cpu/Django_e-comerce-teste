from django.shortcuts import render,redirect
from carrinho.models import ItemCarrinho,Carrinho
from e_comerce.services import erp as erp_service

def _get_cart_for_request(request):
    if request.user.is_authenticated:
        return Carrinho.objects.filter(usuario=request.user).first()
    
    session_key = request.session.session_key
    if not session_key:
        return None
    
    return Carrinho.objects.filter(session_key=session_key).first()


def carrinho(request):
    carrinho=_get_cart_for_request(request)

    if not carrinho:
        itens=[]
        subtotal=0
    else:
        itens=carrinho.itens.select_related('produto').all() # type: ignore
        subtotal = 0

        for item in itens:
            produto=item.produto

            if produto.erp_id:
                availabity = erp_service.check_availability(
                    produto.erp_id,
                    item.quantidade
                )

                if not availabity['available']:
                    item.quantidade=availabity['stock']
                    item.save()

            subtotal += produto.preco * item.quantidade
            
    context = {
        'is_index': False,
        'Items':itens,
        'subtotal':subtotal,
    }
    return render(request, 'carrinho/carrinho.html', context)
