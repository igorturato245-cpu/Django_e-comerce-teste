from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from carrinho.models import ItemCarrinho

def atualizar_quantidade(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantidade = int(request.POST.get("quantidade"))

        item = get_object_or_404(ItemCarrinho, id=item_id)

        item.quantidade = max(1, quantidade)
        item.save()

        subtotal = sum(
            i.produto.preco * i.quantidade
            for i in ItemCarrinho.objects.all()
        )

        return JsonResponse({
            "quantidade": item.quantidade,
            "subtotal": float(subtotal),
        })
