from django.urls import path
from e_comerce.views import view_principal
from e_comerce.views import view_produto
from carrinho.view import view_carrinho

app_name='produtos'

urlpatterns = [
    path('', view_principal.index, name='index'),
    path('produto/<int:produto_id>', view_produto.produto, name='produto'),
]
