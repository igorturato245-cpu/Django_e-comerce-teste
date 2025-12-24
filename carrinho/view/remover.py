from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho
from carrinho.view.view_carrinho import _get_cart_for_request

def remover_do_carrinho(request, item_id):
    if request.method == "POST":
        cart = _get_cart_for_request(request)
        item = get_object_or_404(ItemCarrinho, id=item_id,carrinho=cart)
        item.delete()

        subtotal = sum(
            i.produto.preco * i.quantidade
            for i in cart.itens.select_related('produto').all() #type:ignore
        ) if cart else 0

        itens_restantes=cart.itens.count() if cart else 0 #type:ignore

        return JsonResponse({
            "success": True,
            "subtotal": float(subtotal),
            "itens_restantes": itens_restantes
        })
