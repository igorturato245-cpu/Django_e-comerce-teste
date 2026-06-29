from django.contrib import admin
from e_comerce.models import *

class CarroselImagens(admin.TabularInline):
    model=ProdutoImagens
    extra=1

@admin.register(Produto)
class Produtoadmin(admin.ModelAdmin):
    list_display=('category','name','preco','preco_promocional','disponivel','ofertas_do_dia',)
    list_editable=('ofertas_do_dia',)
    ordering=('-id',)
    list_per_page=10
    list_max_show_all=200
    list_display_links=('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines=[
        CarroselImagens,
    ]
    
    def exibir_preco(self,obj):
        return f'{obj.get_preco()}'
    
    exibir_preco.short_descripiton='Preço Atual'

@admin.register(Category)
class Categoryadmin(admin.ModelAdmin):
    list_display='name','slug',
    ordering='-id',
    
@admin.register(Avaliacao_produto)
class Avaliacao_produto_admin(admin.ModelAdmin):
    list_display='nota_site','nota_produto'
    
@admin.register(TokenFornecedor)
class TokenFornecedorAdmin(admin.ModelAdmin):
    list_display = 'access_token','refresh_token'