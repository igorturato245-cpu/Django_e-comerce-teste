from django.contrib import admin
from carrinho.models import Carrinho, ItemCarrinho

@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display=('id','criado_em',)
    ordering=('-id',)
    list_filter=('criado_em',)

@admin.register(ItemCarrinho)
class ItemCarrinhoAdmin(admin.ModelAdmin):
    list_display=('id','carrinho','produto','quantidade',)
    ordering=('-id',)
    list_filter=('carrinho','produto',)
