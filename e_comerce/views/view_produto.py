from django.shortcuts import render,get_object_or_404,redirect
from e_comerce.models import Produto

def produto(request,produto_id):
    sigle_product=get_object_or_404(Produto,pk=produto_id,disponivel=True)
    ofertas_do_dia=Produto.objects.filter(ofertas_do_dia=True,disponivel=True)

    context={
        'produto':sigle_product,
        'ofertas_do_dia':ofertas_do_dia,
    }

    return render(
        request,
        'e_comerce/produto.html',
        context,
    )