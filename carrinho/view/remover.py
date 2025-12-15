from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho

def remover_do_carrinho(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(ItemCarrinho, id=item_id)
        item.delete()

        subtotal = sum(
            i.produto.preco * i.quantidade
            for i in ItemCarrinho.objects.all()
        )

        return JsonResponse({
            "success": True,
            "subtotal": float(subtotal),
            "itens_restantes": ItemCarrinho.objects.count()
        })
