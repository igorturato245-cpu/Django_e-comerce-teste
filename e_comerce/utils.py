import logging
from django.db import transaction
from django.db.models import Q
from pagamentos.models import Pedido,PedidoItem
from .models import Produto

logger = logging.getLogger(__name__)

def atualiza_estoque_pago(pedido_id):
    with transaction.atomic():
        pedido = Pedido.objects.select_for_update().get(pk=pedido_id)
        
        if pedido.estoque_baixado:
            return
        
        itens = pedido.items.select_related('produto').all() #type:ignore
        
        for item in itens:

            try:
                if item.produto:
                    item.produto.atualiza_estoque_paid(item.quantidade)
                else:
                    logger.error(f"ALERTA: Produto {item.id} não encontrado no banco.")

            except Exception as e:
                logger.error(f"ERRO no item {item.id}: {str(e)}")

        pedido.estoque_baixado = True
        pedido.save(update_fields=['estoque_baixado'])
        
        
def atualiza_estoque_returned(pedido_id):
    with transaction.atomic():
        pedido=Pedido.objects.select_related().get(pk=pedido_id)
        
        if not pedido.estoque_baixado:
            return
        
        item_returned=pedido.items.select_related('produto').all() #type:ignore
        
        for itens in item_returned:
            
            try:

                if itens.produto:
                    itens.produto.atualiza_estoque_devolvido(itens.quantidade)
                else:
                    logger.error(f'Produto com ID {itens.produto_id} não encontrado para atualização de estoque.')

            except:
                logger.error('Erro ao atualizar estoque')
                
        pedido.estoque_baixado=False
        pedido.save(update_fields=['estoque_baixado'])