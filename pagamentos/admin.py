from django.contrib import admin
from pagamentos.models import *

class PedidoItemTabular(admin.TabularInline):
    model=PedidoItem
    extra=1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display=('id','usuario','status','payment_reference','erp_order_id','erp_status',)
    list_display_links=('id','usuario',)
    ordering=('-id',)
    list_per_page=10
    list_max_show_all=200
    inlines=[
        PedidoItemTabular,
        ]

@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    pass