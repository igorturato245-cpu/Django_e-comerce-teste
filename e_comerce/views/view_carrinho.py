from django.shortcuts import render,get_object_or_404,redirect
from e_comerce.models import Produto

def carrinho(request,produto_id):
    sigle_product=get_object_or_404(Produto,pk=produto_id,disponivel=True)

    context={
        'produto':sigle_product,
    }

    return render(
        request,
        'e_comerce/carrinho.html',
        context,
    )