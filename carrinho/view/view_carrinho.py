from django.shortcuts import render
from carrinho.models import ItemCarrinho

def carrinho(request):
    itens=ItemCarrinho.objects.all()

    subtotal = sum(
        item.produto.preco * item.quantidade
        for item in itens
    )
    
    context = {
        'is_index': False,
        'Items':itens,
        'subtotal':subtotal,
    }
    return render(request, 'carrinho/carrinho.html', context)
