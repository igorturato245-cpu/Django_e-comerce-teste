from django.contrib import admin
from e_comerce.models import *

@admin.register(Produto)
class Produtoadmin(admin.ModelAdmin):
    list_display='category','name','preco','disponivel',
    ordering='-id',
    list_per_page=10
    list_max_show_all=200
    list_display_links='name',

@admin.register(Category)
class Categoryadmin(admin.ModelAdmin):
    list_display='name',
    ordering='-id',