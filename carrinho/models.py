from django.db import models
from e_comerce.models import Produto
from django.contrib.auth.models import User
from utils import utils
from decimal import Decimal
from e_comerce.models import Produto
from django.db.models import F, Sum,DecimalField, ExpressionWrapper
from django.forms import ValidationError

class Carrinho(models.Model):
    usuario=models.ForeignKey(User,null=True,blank=True,db_index=True,on_delete=models.CASCADE)
    session_key=models.CharField(max_length=40,null=True,blank=True,db_index=True,unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em=models.DateTimeField(auto_now=True)
    
    def total(self):
        total = self.itens.aggregate(#type:ignore
            total=Sum(
                ExpressionWrapper(
                    F('preco_unitario') * F('quantidade'),
                    output_field=DecimalField()
                )
            )
        )['total']

        return total or Decimal('0.00')

    def __str__(self) -> str:
        if self.usuario:
            return f'Carrinho de {self.usuario.username} - criado em {self.criado_em.strftime("%d/%m/%Y %H:%M:%S")}'
        if self.session_key:
            return f'Carrinho session {self.session_key} - criado em {self.criado_em.strftime("%d/%m/%Y %H:%M:%S")}'
        return self.criado_em.strftime("Carrinho criado em %d/%m/%Y às %H:%M:%S")
    
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, related_name='itens', on_delete=models.CASCADE)
    produto= models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    
    def atualiza_qtd(self,qtd):
        quantidade=max(1,qtd)
        
        MAX_QTD=10
        
        limite_real=min(MAX_QTD,self.produto.estoque)
        
        if quantidade >limite_real:
            self.quantidade=limite_real
        
        else:
            self.quantidade=quantidade
        
        return self.quantidade
    
    def save(self,*args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario=self.produto.get_preco()
            
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.produto.name} - {self.quantidade}'