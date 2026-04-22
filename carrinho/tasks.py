from celery import shared_task
from .models import Carrinho
from django.utils.timezone import now
from datetime import timedelta


@shared_task
def executa_limpeza_carrinhos():
    limite=now() - timedelta(days=7)
        
    limite_logado=now() - timedelta(days=30)
        
    deletados,_=Carrinho.objects.filter(
            criado_em__lt=limite,
            usuario__isnull=True,
            itens__isnull=True,
        ).delete()
        
    
    deletados_logado,_=Carrinho.objects.filter(
            criado_em__lt=limite_logado,
            usuario__isnull=False,
        ).filter(pedido__isnull=True).delete()


    return f"Limpeza concluída: {deletados} anônimos e {deletados_logado} logados removidos."


@shared_task
def limpar_carrinhos_abandonados_task():
    return executa_limpeza_carrinhos()