from django.db import models
from e_comerce.models import Produto
from django.contrib.auth.models import User

class Carrinho(models.Model):
    usuario=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    session_key=models.CharField(max_length=40,null=True,blank=True,db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

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

    def __str__(self) -> str:
        return f'{self.produto.name} - {self.quantidade}'