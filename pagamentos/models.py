from django.db import models
from django.contrib.auth.models import User
from carrinho.models import Carrinho

class Pedido(models.Model):
    STATUS_CHOICES=[
        ('pending','Pendente'),
        ('paid','Pago'),
        ('cancelled','Cancelado'),
        ('refunded','Reembolsado'),
        ('erp_sent','Enviado ao ERP'),
        ('erp_confirmed','Confirmado no ERP'),
        ('erp_error','Erro no ERP'),
    ]
    ERP_STATUS_CHOICES=[
        ('sending','Enviando'),
        ('sent','Enviado'),
        ('confirmed','Confirmado'),
        ('error','Erro'),
    ]

    usuario = models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL)
    carrinho=models.ForeignKey(Carrinho,null=True,blank=True,on_delete=models.SET_NULL)
    total=models.DecimalField(max_digits=10, decimal_places=2 )
    status=models.CharField(max_length=32,choices=STATUS_CHOICES,default='pending')
    created_at=models.DateTimeField(auto_now_add=True)
    payment_reference=models.CharField(max_length=128,null=True,blank=True,db_index=True)
    erp_order_id = models.CharField(max_length=128,null=True,blank=True)
    erp_status=models.CharField(max_length=32,choices=ERP_STATUS_CHOICES,null=True,blank=True)
    metadata=models.JSONField(null=True,blank=True)


class PedidoItem(models.Model):
    pedido=models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    produto_id=models.CharField(max_length=128,null=True,blank=True)
    produto_name=models.CharField(max_length=255)
    quantidade=models.PositiveBigIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)