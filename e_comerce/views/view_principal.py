from django.shortcuts import render,get_list_or_404,redirect
from e_comerce.models import Produto

def index(request):
    produtos=Produto.objects.order_by('-id')

    context={
        'produtos':produtos
    }

    return render(
        request,
        'e_comerce/index.html',
        context,
    )