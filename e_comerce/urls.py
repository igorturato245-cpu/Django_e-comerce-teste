from django.urls import path
from e_comerce import views

app_name='Produtos'

urlpatterns = [
    path('',views.index,name='index')
]
