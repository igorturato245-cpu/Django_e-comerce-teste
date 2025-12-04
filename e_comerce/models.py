from django.db import models
from django.urls import reverse

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
    estoque=models.PositiveIntegerField('Estoque',default=0)
    disponivel=models.BooleanField('Disponível',default=True)
    ofertas_do_dia=models.BooleanField('Ofertas do dia', default=False)
    imagem=models.ImageField('Imagem',upload_to='produtos/%/%/%d',blank=True,null=True)
    criado=models.DateTimeField('Criado em' ,auto_now_add=True)
    atualizado=models.DateTimeField('Atualizado em' ,auto_now=True)

    class Meta:
        verbose_name='Produto'
        verbose_name_plural='Produtos'
        ordering=['-criado']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("produto_detail", args=[self.slug])
    
    