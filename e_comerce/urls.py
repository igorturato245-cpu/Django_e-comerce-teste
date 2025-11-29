from django.urls import path
from e_comerce.views import view_principal
from e_comerce.views import view_produto
from e_comerce.views import view_carrinho

app_name='Produtos'

urlpatterns = [
    path('', view_principal.index, name='index'),
    path('produto/<int:produto_id>', view_produto.produto, name='Produto'),
    path('carrinho/<int:carrinho_id>',view_carrinho.carrinho,name='carrinho')
]
