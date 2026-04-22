from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import Pedido,Solicitacao_reembolso
from .utils import enviar_email_status_pedido,enviar_email_status_erp_pedido,enviar_email_status_reembolso,enviar_email_pedido_recebido,enviar_email_cancelamento_direto
from .tasks import send_order_cancelled_to_erp_task

@receiver(pre_save,sender=Pedido)
def capturar_status_anterior(sender,instance,**kwargs):
    if instance.pk:
        try:
            old_instance=Pedido.objects.get(id=instance.pk)
            instance._old_status=old_instance.status
            instance._old_erp_status=old_instance.erp_status
        except Pedido.DoesNotExist:
            instance._old_status=None
            instance._old_erp_status=None
    else:
        instance._old_status=None
        instance._old_erp_status=None


@receiver(post_save,sender=Pedido)
def disparar_email_apos_mudanca_status(sender,instance,created,**kwargs):
    if created:
        enviar_email_pedido_recebido(instance)
        return
    
    status_mudou=getattr(instance,'_old_status',None) != instance.status
    erp_mudou = getattr(instance,'_old_erp_status',None) != instance.erp_status
    
    
    if status_mudou:
        enviar_email_status_pedido(instance)
        
    if erp_mudou:
        enviar_email_status_erp_pedido(instance)

@receiver(post_save, sender=Pedido)
def disparar_email_cancelamento_direto(sender,instance,created,**kwargs):
    if instance.status == 'cancelled' and instance._old_status != 'cancelled':
        enviar_email_cancelamento_direto(instance)
    
@receiver(post_save,sender=Solicitacao_reembolso)
def disparar_email_apos_mudanca_reembolso(sender,instance,created,**kwargs):
    enviar_email_status_reembolso(instance, instance.pedido)
    
@receiver(post_save, sender=Pedido)
def apagar_carrinho_pago(sender,instance,created,**kwargs):
    if instance.status == 'paid':
        if instance.carrinho:
            instance.delete_cart_paid()
            
        
            
@receiver(post_save, sender=Solicitacao_reembolso)
def alterar_status_pedido_apos_solicitacao(sender,instance, created,**kwargs):
    if created:
        pedido=instance.pedido
        pedido.status='cancelled'
        pedido.save(update_fields=['status'])
        
        
@receiver(post_save, sender=Solicitacao_reembolso)
def enviar_order_erp_reembolso(sender,instance,created,**kwargs):
    if instance.status == 'approved':
        pedido=instance.pedido
        pedido.refresh_from_db() 
        
        if pedido.erp_status != 'cancelled':
            #send_order_cancelled_to_erp_task.delay(pedido.id) #type:ignore
            pass
        else:
            print(f"Pedido {pedido.id} já consta como cancelado no ERP. Ignorando disparo.")