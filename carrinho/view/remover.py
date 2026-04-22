from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho
from carrinho.view.view_carrinho import _get_cart_for_request
from utils import utils
from decimal import Decimal,ROUND_HALF_UP

def remover_do_carrinho(request, item_id):
    if request.method == "POST":
        cart = _get_cart_for_request(request)
        item = get_object_or_404(ItemCarrinho, id=item_id,carrinho=cart)
        item.delete()
        
        itens=cart.itens.all() #type:ignore        
        subtotal=cart.total()

        itens_restantes=len(itens)

        return JsonResponse({
            "success": True,
            "subtotal": float(subtotal),
            "subtotal_format":utils.formata_preco(subtotal),
            "itens_restantes": itens_restantes
        })
