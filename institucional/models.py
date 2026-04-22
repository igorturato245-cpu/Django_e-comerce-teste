from django.db import models

class Contato_user(models.Model):
    nome=models.CharField('Nome',max_length=35)
    email=models.EmailField('Email')
    texto=models.CharField('Área de contato',max_length=400)
    
    class Meta:
        verbose_name='Contato'
        