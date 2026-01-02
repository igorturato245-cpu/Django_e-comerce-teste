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


        pedido.erp_status='sending'
        pedido.save(update_fields=['erp_status'])

        resp=erp_integration.send_order(pedido)

        pedido.erp_order_id=resp.get('id') or resp.get('order_id')
        pedido.erp_status=resp.get('status') or 'sent'
        pedido.save(update_fields=['erp_order_id', 'erp_status'])

        logger.info(f'Pedido {pedido_id} enviado para ERP. ID:{pedido.erp_order_id}')

    except Exception as exc:
        logger.error(f'Erro ao enviar pedido {pedido_id} para ERP:{exc}')

        try:
            self.retry(exc=exc,countdown=60 * (2**(self.request.retries)))
        except self.MaxRetriesExceededError:
            pedido.erp_status='erp_error'
            pedido.save(update_fields=['erp_status'])
            logger.error(f'Pedido {pedido_id}:Máximo de tentativas excedido')