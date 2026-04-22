from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho
from carrinho.view.view_carrinho import _get_cart_for_request
from utils import utils
from decimal import Decimal,ROUND_HALF_UP

def atualizar_quantidade(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        try:
            quantidade = int(request.POST.get("quantidade"))
        except(TypeError,ValueError):
            quantidade=1
        
        cart=_get_cart_for_request(request)
        item = get_object_or_404(ItemCarrinho.objects.select_related('produto'), id=item_id,carrinho=cart)

        item.atualiza_qtd(quantidade)
        item.save()
        
        subtotal=cart.total()
        
        return JsonResponse({
            "quantidade": item.quantidade,
            "subtotal": float(subtotal),
            "subtotal_format":utils.formata_preco(subtotal)
        })
