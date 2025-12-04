from django.shortcuts import render,get_list_or_404,redirect
from e_comerce.models import Produto

def index(request):
    produtos=Produto.objects.order_by('-id')
    ofertas_do_dia=Produto.objects.filter(ofertas_do_dia=True,disponivel=True)[:8]

    context={
        'produtos':produtos,
        'ofertas_do_dia':ofertas_do_dia,
    }

    return render(
        request,
        'e_comerce/index.html',
        context,
    )