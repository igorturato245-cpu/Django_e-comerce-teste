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
        item = get_object_or_404(ItemCarrinho, id=item_id,carrinho=cart)

        item.quantidade = max(1, quantidade)
        item.save()

        subtotal=Decimal('0.00')

        for i in cart.itens.select_related('produto').all(): #type:ignore
            preco=i.produto.preco_promocional or i.produto.preco
            preco=Decimal(str(preco))
            subtotal+=preco*i.quantidade

        subtotal=subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return JsonResponse({
            "quantidade": item.quantidade,
            "subtotal": float(subtotal),
            "subtotal_format":utils.formata_preco(subtotal)
        })
