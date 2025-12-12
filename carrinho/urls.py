from django.urls import path
from carrinho.view import view_carrinho

app_name='carrinho'

urlpatterns = [
    path('',view_carrinho.carrinho,name='carrinho')
]
