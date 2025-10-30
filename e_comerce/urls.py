from django.urls import path
from e_comerce.views import view_principal

app_name='Produtos'

urlpatterns = [
    path('',view_principal.index,name='index')
]
