from django.shortcuts import render,get_object_or_404,redirect
from e_comerce.models import Produto

def produto(request,categoria_slug,produto_slug):
    sigle_product=get_object_or_404(Produto.objects.select_related('category'),slug=produto_slug,category__slug=categoria_slug,disponivel=True)
    ofertas_do_dia=Produto.objects.filter(ofertas_do_dia=True,disponivel=True).select_related('category')

    context={
        'is_index':False,
        'produto':sigle_product,
        'ofertas_do_dia':ofertas_do_dia,
    }

    return render(
        request,
        'e_comerce/produto.html',
        context,
    )