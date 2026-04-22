from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho
from carrinho.view.view_carrinho import _get_cart_for_request

def atualizar_qtd(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantidade = int(request.POST.get("quantidade"))
        cart=_get_cart_for_request(request)

        item = get_object_or_404(ItemCarrinho.objects.select_related('produto'),id=item_id)

        item.quantidade=max(1,quantidade)
        item.save()
        
        subtotal=cart.total()

        return JsonResponse({
            'quantidade':item.quantidade,
            'subtotal':float(subtotal),
        })
    
    