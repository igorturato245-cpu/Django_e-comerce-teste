from django.db import models
from django.contrib.auth.models import User
from carrinho.models import Carrinho
from django.utils import timezone
from datetime import timedelta
from e_comerce.services import erp as erp_service
from decimal import Decimal

class Pedido(models.Model):
    STATUS_CHOICES=[
        ('pending','Pendente'),
        ('paid','Pago'),
        ('cancelled','Cancelado'),
        ('refunded','Reembolsado'),
        ('refusal','Reembolso negado'),
        ('erp_sent','Enviado ao ERP'),
        ('erp_confirmed','Confirmado no ERP'),
        ('erp_error','Erro no ERP'),
    ]
    ERP_STATUS_CHOICES=[
        ('pending','Pendente'),
        ('received','Recebido'),
        ('paid','Pago'),
        ('sending','Enviando'),
        ('sent','Enviado'),
        ('confirmed','Confirmado'),
        ('cancelled','Cancelado'),
        ('return','Devolução'),
        ('return_refusal','Devolução negada'),
        ('returned','Devolvido'),
        ('error','Erro'),
    ]

    usuario = models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL)
    carrinho=models.ForeignKey(Carrinho,null=True,blank=True,on_delete=models.SET_NULL)
    total=models.DecimalField(max_digits=10, decimal_places=2 )
    valor_frete=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    total_com_frete=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    status=models.CharField(max_length=32,choices=STATUS_CHOICES,default='pending')
    estoque_baixado=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    payment_reference=models.CharField(max_length=128,null=True,blank=True,db_index=True)
    erp_order_id = models.CharField(max_length=128,null=True,blank=True)
    erp_status=models.CharField(max_length=32,choices=ERP_STATUS_CHOICES,null=True,blank=True)
    tracking_code=models.CharField("Código de rastreio", max_length=64,null=True,blank=True)
    tracking_url=models.URLField("URL de rastreio",null=True,blank=True)
    data_envio=models.DateTimeField("Data de envio", null=True,blank=True)
    metadata=models.JSONField(null=True,blank=True)
    
    def delete_cart_paid(self):
        if self.status == 'paid' and self.carrinho:
            carrinho_id=self.carrinho.pk
            self.carrinho=None 
            self.save(update_fields=['carrinho'])
            
            from carrinho.models import Carrinho
            Carrinho.objects.filter(pk=carrinho_id).delete()
            return True
        return False
    
    @property
    def pode_cancelar_direto(self):
        return self.status in ['paid','erp_sent','erp_confirmed'] and self.erp_status in ['paid','confirmed','sending']
    
    @property
    def pode_solicitar_reembolso(self):
        return self.status in ['erp_confirmed'] and self.erp_status in ['sent', 'received'] 
    
    def ja_avaliado(self):
        from e_comerce.models import Avaliacao_produto
        return Avaliacao_produto.objects.filter(usuario=self.usuario, pedido=self).exists()
    
    @property
    def prazo_arrependimento(self):
        return timezone.now() < self.created_at + timedelta(days=7)
    
    @classmethod
    def calcula_total(cls,cep,itens,total):
        calcular_frete=erp_service.get_shipping_quote(cep,itens)
    
        if calcular_frete:
            valor_frete=Decimal(str(calcular_frete.get('price','0')))
            prazo_entrega=calcular_frete.get('delivery_days','0')
        else:
            valor_frete=Decimal('25.00')
            prazo_entrega=10
        
        total_com_frete=total + valor_frete
        
        
        return {
            'valor_frete': valor_frete,
            'prazo_entrega': prazo_entrega,
            'total_com_frete': total_com_frete,
            'total_produtos': total
        }
        


class PedidoItem(models.Model):
    pedido=models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    produto = models.ForeignKey('e_comerce.Produto',on_delete=models.SET_NULL,null=True,blank=True)
    produto_id_string=models.CharField(max_length=128,null=True,blank=True)
    produto_name=models.CharField(max_length=255)
    quantidade=models.PositiveBigIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    
    
class Solicitacao_reembolso(models.Model):
    STATUS_CHOICES=[
        ('pending','Pendente'),
        ('approved','Aprovado'),
        ('rejected','Rejeitado'),
        ('completed', 'Concluído'),
    ]
    
    
    pedido=models.ForeignKey(Pedido, related_name='produtos_reembolso', on_delete=models.CASCADE)
    motivo=models.CharField(max_length=50)
    feedback=models.TextField(null=True,blank=True, max_length=300)
    evidencias=models.FileField(upload_to="evidencias-devolucao/")
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')