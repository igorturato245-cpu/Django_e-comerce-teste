from django.urls import path
from carrinho.view import qtd, view_carrinho,add_carrinho,remover

app_name='carrinho'

urlpatterns = [
    path('',view_carrinho.carrinho,name='carrinho'),
    path('adicionar/<int:produto_id>/', add_carrinho.adicionar_ao_carrinho, name='adicionar'),
    path('atualizar-quantidade/', qtd.atualizar_quantidade, name='atualizar_quantidade'),
    path('remover/<int:item_id>/', remover.remover_do_carrinho, name='remover'),
]
