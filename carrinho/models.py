from django.db import models
from e_comerce.models import Produto

class Carrinho(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.criado_em.strftime("Carrinho criado em %d/%m/%Y às %H:%M:%S")
    
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, related_name='itens', on_delete=models.CASCADE)
    produto= models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.produto.name} - {self.quantidade}'