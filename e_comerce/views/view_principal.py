from django.shortcuts import render,get_list_or_404,redirect
from django.core.paginator import Paginator
from e_comerce.models import Produto

def index(request):
    produtos=Produto.objects.filter(show=True).order_by('-id')

    paginador=Paginator(produtos,20)
    page_number=request.GET.get('page')
    page_obj=paginador.get_page(page_number)

    context={
        'page_obj':page_obj
    }

    return render(
        request,
        'e_comerce/templates/index.html',
        context,
    )


def produto(request,produto_id):
    sigle_product=get_list_or_404(Produto,pk=produto_id,show=True)

    context={
        'produto':sigle_product,
    }

    render(
        request,
        'e_comerce/templates/produto.html',
        context,
    )