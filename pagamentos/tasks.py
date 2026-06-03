from celery import shared_task
import logging
from pagamentos.models import Pedido
from pagamentos.integrations import erp as erp_integration


logger=logging.getLogger(__name__)


@shared_task(bind=True,max_retries=5,default_retry_delay=60)
def send_order_to_erp_task(self,pedido_id):
    try:
        pedido=Pedido.objects.select_related('usuario').prefetch_related('items').get(id=pedido_id)
        logger.info(f'Iniciando envio do pedido {pedido_id} para ERP')
        
        if pedido.erp_order_id and pedido.erp_status == 'sent':
            logger.warning(f'Pedido {pedido.pk} já foi enviado para o ERP, pulando reenvio')
            return


        Pedido.objects.filter(id=pedido_id).update(erp_status='sending')

        resp=erp_integration.send_order(pedido)

        Pedido.objects.filter(id=pedido_id).update(erp_order_id=resp.get('id') or resp.get('order_id'), erp_status=resp.get('status') or 'sent')

        logger.info(f'Pedido {pedido_id} enviado para ERP. ID:{pedido.erp_order_id}')

    except Exception as exc:
        logger.error(f'Erro ao enviar pedido {pedido_id} para ERP:{exc}')

        try:
            self.retry(exc=exc,countdown=60 * (2**(self.request.retries)))
        except self.MaxRetriesExceededError:
            Pedido.objects.filter(id=pedido_id).update(erp_status='error')
            logger.error(f'Pedido {pedido_id}:Máximo de tentativas excedido')
            

@shared_task(bind=True,max_retries=5,default_retry_delay=60)
def send_order_cancelled_to_erp_task(self,pedido_id):
    try:
        pedido=Pedido.objects.select_related('usuario').prefetch_related('items').get(id=pedido_id)
        logger.info(f'Iniciando envio de cancelamento do pedido {pedido_id} para ERP')
        
        resp=erp_integration.send_order_cancelled(pedido)
        
        pedido.erp_order_id=resp.get('id') or resp.get('order_id')
        pedido.erp_status=resp.get('status') or 'cancelled'
        pedido.save(update_fields=['erp_order_id', 'erp_status'])
        
        logger.info(f'Cancelamento do pedido {pedido_id} enviado para o ERP. ID:{pedido.erp_order_id}')
    
    except Exception as e:
        logger.error(f'Erro ao enviar pedido de cancelamento para o ERP. Pedido {pedido_id}:{e}')
        
        try:
            self.retry(exc=e,countdown=60 * (2**(self.request.retries)))
        except self.MaxRetriesExceededError:
            Pedido.objects.filter(id=pedido_id).update(erp_status='error')
            logger.error(f'Pedido {pedido_id}:Máximo de tentativas alcançada, não foi possível realizar o cancelamento no ERP')
            
            
            
@shared_task
def check_all_orders_tracking_task():
    pedidos_ids=Pedido.objects.filter(erp_status='sent',tracking_code__isnull=True).values_list('id',flat=True)
    
    for p_id in pedidos_ids:
        update_individual_tracking_task.delay(p_id)
            
@shared_task
def update_individual_tracking_task(self,pedido_id):
    
    try:
        pedido=Pedido.objects.select_related('usuario').get(id=pedido_id)
        
        info=erp_integration.get_order_info(pedido.erp_order_id)
            
        if info.get('tracking_code'):
            pedido.tracking_code=info['tracking_code']
            pedido.tracking_url=info.get('tracking_url')
            pedido.data_envio=info.get('data_envio')
            pedido.save(update_fields=['tracking_code','tracking_url','data_envio'])
                
    except Exception as e:
        logger.error(f'Erro ao consultar informações de rastreio do pedido {pedido.pk} no ERP:{e}')