from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho
from carrinho.view.view_carrinho import _get_cart_for_request

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

        subtotal = sum(
            i.produto.preco * i.quantidade
            for i in cart.itens.select_related('produto').all() #type:ignore
        )

        return JsonResponse({
            "quantidade": item.quantidade,
            "subtotal": float(subtotal),
        })
