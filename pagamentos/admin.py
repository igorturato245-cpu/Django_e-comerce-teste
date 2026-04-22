from django.contrib import admin
from pagamentos.models import *
from django.db.models import Sum

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
    
    
    def lucro_estimado(self,obj):
        if obj.status in ['paid','erp_sent','erp_confirmed']:
            return 'R$ 30,00'
        return 'R$ 0,00'
    
    lucro_estimado.short_descripiton = 'Lucro (R$)'
    
    
    def chengelist_view(self,request,extra_context=None):
        response=super().changelist_view(request,extra_context)
        
        if hasattr(response,'context_data') and response.context_data is not None:
            
            cl = response.context_data.get('cl')
            
            if cl:
                qs=cl.queryset
                vendas_validas=qs.filter(status__in=['paid','erp_sent','erp_confirmed']).count()
                
                lucro_total=vendas_validas*30
                
                response.context_data['total_lucro_pessoal']=lucro_total
            
            return response

@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Solicitacao_reembolso)
class Solicitar_reembolsoAdmin(admin.ModelAdmin):
    list_display=('id','pedido','motivo','status')
    list_display_links=('id','pedido',)
    ordering=('-id',)
    list_per_page=10
    list_max_show_all=200