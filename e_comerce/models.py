from django.db import models
from django.urls import reverse
from utils import utils

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
    preco_promocional=models.FloatField(default=0, verbose_name='Preço promocional')
    estoque=models.PositiveIntegerField('Estoque',default=0)
    disponivel=models.BooleanField('Disponível',default=True)
    ofertas_do_dia=models.BooleanField('Ofertas do dia', default=False)
    imagem=models.ImageField('Imagem',upload_to='produtos/%/%/%d',blank=True,null=True)
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

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("produto_detail", args=[self.slug])
    
    def formata_preco(self):
        return utils.formata_preco(self.preco)
    formata_preco.short_description='Preço'

    def formata_preco_promo(self):
        return utils.formata_preco(self.preco_promocional)
    formata_preco_promo.short_description='Preço Promo'
        
    
    