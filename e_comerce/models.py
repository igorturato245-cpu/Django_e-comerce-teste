from django.db import models
from django.urls import reverse
from utils import utils
from django.utils.text import slugify
from decimal import Decimal
from django.db.models import F
from django.db.models.expressions import Combinable
from django.contrib.auth.models import User
from django.db.models import Avg

class Category(models.Model):
    name=models.CharField( 'Nome',max_length=200,unique=True)
    slug=models.SlugField('Slug',max_length=200,unique=True)

    class Meta:
        verbose_name='Categoria'
        verbose_name_plural ='Categorias'
        ordering=['name']

    def __str__(self) -> str:
        return self.name

class Produto(models.Model):
    category=models.ForeignKey(Category,related_name='produtos',on_delete=models.CASCADE)
    name=models.CharField('Nome',max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True)
    descricao=models.TextField('Descrição',blank=True)
    preco=models.DecimalField('Preço',max_digits=10,decimal_places=2)
    preco_promocional=models.DecimalField('Preço promocional',max_digits=10,decimal_places=2,default=Decimal('0.00'))
    estoque=models.PositiveIntegerField('Estoque',default=0)
    disponivel=models.BooleanField('Disponível',default=True)
    ofertas_do_dia=models.BooleanField('Ofertas do dia', default=False)
    imagem=models.ImageField('Imagem',upload_to='produtos/%Y/%m/%d/',blank=True,null=True)
    image_url=models.URLField('Imagem remota', blank=True,null=True)
    criado=models.DateTimeField('Criado em' ,auto_now_add=True)
    atualizado=models.DateTimeField('Atualizado em' ,auto_now=True)

    erp_id=models.CharField('ERP ID', max_length=128,null=True,blank=True,db_index=True)
    remote_price=models.DecimalField(("Preço remoto"), max_digits=10, decimal_places=2,null=True,blank=True)
    remote_stock=models.IntegerField('Estoque remoto', null=True,blank=True)
    last_synced = models.DateTimeField('Última sincronização', null=True,blank=True)

    class Meta:
        verbose_name='Produto'
        verbose_name_plural='Produtos'
        ordering=['-criado']
        indexes=[models.Index(fields=['category','disponivel']),models.Index(fields=['ofertas_do_dia','disponivel'])]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("produto_detail", args=[self.slug])
    
    def formata_preco(self):
        return Decimal(utils.formata_preco(self.preco))
    formata_preco.short_description='Preço'

    def formata_preco_promo(self):
        return Decimal(utils.formata_preco(self.preco_promocional))
    formata_preco_promo.short_description='Preço Promo'
    
    def get_preco(self):
        if self.preco_promocional and self.preco_promocional > Decimal('0.00'):
            return self.preco_promocional
        return self.preco
    
    def atualiza_estoque_paid(self, quantidade):
        if self.estoque < quantidade:
            raise ValueError(f'Estoque insuficiente para o produto:{self.pk}')
        
        self.estoque =F('estoque') - quantidade
        self.remote_stock = F('remote_stock') - quantidade
        self.save(update_fields=['estoque', 'remote_stock'])
        
        self.refresh_from_db()
        
        if self.estoque <= 0:
            Produto.objects.filter(pk=self.pk).update(disponivel=False)
        
    def atualiza_estoque_devolvido(self,quantidade):
        
        self.estoque=F('estoque') + quantidade
        self.remote_stock = F('remote_stock') + quantidade
        self.save(update_fields=['estoque','remote_stock'])
        print('Estoque atualizado')
        self.refresh_from_db()
        
        if self.estoque > 0:
            Produto.objects.filter(pk=self.pk).update(disponivel=True)
        
    @property
    def media_avaliacao(self):
        media=self.avaliacoes.aggregate(Avg('nota_produto'))['nota_produto__avg']#type:ignore

        return round(media,1) if media else 0.0
    
    @property
    def estrelas_cheias(self):
        return range(int(self.media_avaliacao))
    
    @property
    def tem_meia(self):
        return (self.media_avaliacao - int(self.media_avaliacao)) >= 0.5
    
    @property
    def estrelas_vazias(self):
        vazia=5 - int(self.media_avaliacao)
        
        if self.tem_meia:
            vazia -= 1
        return range(vazia)
        

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
    
        # CORREÇÃO: Só tenta comparar se 'estoque' for um número real.
        # Se for uma expressão F() (Combinable), o Django pula essa linha e não trava.
        if not isinstance(self.estoque, Combinable):
            self.disponivel = self.estoque > 0
        
        super().save(*args, **kwargs)
        

class Avaliacao_produto(models.Model):
    usuario=models.ForeignKey(User,on_delete=models.CASCADE)
    pedido=models.ForeignKey('pagamentos.Pedido',on_delete=models.CASCADE)
    produto=models.ForeignKey(Produto,on_delete=models.CASCADE,related_name='avaliacoes') 
    
    nota_site=models.IntegerField(default=5)
    nota_produto=models.IntegerField(default=5)
    comentario=models.TextField(blank=True,null=True)
    data_criaca=models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'Avaliação de {self.usuario.username} para o produto:{self.produto.name}'
    
    
class TokenFornecedor(models.Model):
    access_token=models.TextField()
    refresh_token=models.TextField()
    update_at=models.DateTimeField(auto_now=True)