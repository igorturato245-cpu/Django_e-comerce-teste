from django.urls import path
from pagamentos.views import view_pagamentos

app_name='Pagamentos'

urlpatterns = [
    path('',view_pagamentos.index,name='index')
]
