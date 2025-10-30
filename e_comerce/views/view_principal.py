from django.shortcuts import render
from e_comerce.models import Produto

def index(request):
    produtos=Produto.objects.all()
    context={
        'produtos':produtos
    }

    return render(
        request,
        'e_comerce/templates/index.html',
        context,
    )
