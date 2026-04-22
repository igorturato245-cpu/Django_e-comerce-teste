from django.shortcuts import render,get_list_or_404,redirect
from e_comerce.models import Produto,Category
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db.models import Prefetch


def index(request): 

    categories=Category.objects.prefetch_related(
        Prefetch('produtos',queryset=Produto.objects.filter(disponivel=True),to_attr='lista_produtos')
    ).filter(produtos__disponivel=True).distinct()


    ofertas_do_dia=Produto.objects.filter(ofertas_do_dia=True,disponivel=True).select_related('category')[:5]

    context={
        'is_index':True,
        'categorias':categories,

        'ofertas_do_dia':ofertas_do_dia,
    }

    return render(
        request,
        'e_comerce/index.html',
        context,
    )