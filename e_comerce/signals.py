from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import atualiza_estoque_pago,atualiza_estoque_returned
from pagamentos.models import Pedido

@receiver(post_save, sender=Pedido)
def atualiza_estoque(sender,instance,created,**kwargs):
    if instance.status == 'paid' and not instance.estoque_baixado:
        atualiza_estoque_pago(instance.id)
        
@receiver(post_save, sender=Pedido)
def atualiza_estoque_devolvido(sender,instance,created,**kwargs):
        
    if instance.erp_status == 'returned' and instance.estoque_baixado:
        atualiza_estoque_returned(instance.id)

    