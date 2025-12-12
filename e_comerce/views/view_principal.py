from django.shortcuts import render,get_list_or_404,redirect
from e_comerce.models import Produto

def index(request):
    perfumes=Produto.objects.filter(category__slug='perfume-',disponivel=True)

    sabonetes=Produto.objects.filter(category__slug='sabonete-',disponivel=True)
    produto_de_limpeza=Produto.objects.filter(category__slug='limpeza-',disponivel=True)

    ofertas_do_dia=Produto.objects.filter(ofertas_do_dia=True,disponivel=True)[:5]

    context={
        'is_index':True,
        'perfumes':perfumes,
        'sabonetes':sabonetes,
        'produto_de_limpeza':produto_de_limpeza,

        'ofertas_do_dia':ofertas_do_dia,
    }

    return render(
        request,
        'e_comerce/index.html',
        context,
    )