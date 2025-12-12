from django.shortcuts import render
from e_comerce.models import Produto

def carrinho(request):
    itens=Produto.objects.all()
    
    context = {
        'is_index': False,
        'itens':itens,
    }
    return render(request, 'carrinho/carrinho.html', context)
