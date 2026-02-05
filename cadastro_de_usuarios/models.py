from utils.validacpf import valida_cpf
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User

class Perfil(models.Model):
    #Perfil:
    usuario=models.ForeignKey(User, null=True,on_delete=models.CASCADE)
    idade=models.IntegerField()
    data_de_nascimento=models.DateField()
    telefone=models.CharField(max_length=15)
    cpf=models.CharField(max_length=11)
    endereco=models.CharField(max_length=50)
    numero=models.CharField(max_length=5)
    complemento=models.CharField(max_length=30)
    bairro=models.CharField(max_length=30)
    cep=models.CharField(max_length=8)
    cidade=models.CharField(max_length=30)
    estado=models.CharField(max_length=2,default="Sp",choices=(
        ('AC','Acre'),
        ('AL','Alagoas'),
        ('AP','Amapá'),
        ('AM','Amazonas'),
        ('BA','Bahia'),
        ('CE','Ceará'),
        ('DF','Distrito Federal'),
        ('ES','Espírito Santo'),
        ('GO','Goiás'),
        ('MA','Maranhão'),
        ('MT','Mato Grosso'),
        ('MS','Mato Grosso do Sul'),
        ('MG','Minas Gerais'),
        ('PA','Pará'),
        ('PB','Paraíba'),
        ('PR','Paraná'),
        ('PE','Pernambuco'),
        ('PI','Piauí'),
        ('RJ','Rio de Janeiro'),
        ('RN','Rio Grande do Norte'),
        ('RS','Rio Grande do Sul' ),
        ('RO','Rondônia'),
        ('RR','Roraima'),
        ('SC','Santa Catarina'),
        ('SP','São Paulo'),
        ('SE','Sergipe'),
        ('TO','Tocantins' ),
    ))

    def __str__(self):
        return f'{self.usuario}'
    
    def clean(self):
        error_messages={}
        
        cpf_enviado=self.cpf or None
        cpf_salvo=None
        perfil=Perfil.objects.filter(cpf=cpf_enviado).first()
        
        if perfil:
            cpf_salvo=perfil.cpf
            
            if cpf_enviado is not None and self.pk != perfil.pk:
                error_messages['cpf']='CPF já cadastrado.'

        if not valida_cpf(self.cpf):
            error_messages['cpf']='Digite um CPF válido.'

        if not self.cep.isdigit() or len(self.cep) != 8:
            error_messages['cep']='CEP inválido.Digite apenas números.'

        if error_messages:
            raise ValidationError(error_messages)
        
    class Meta:
        verbose_name='Perfil'
        verbose_name_plural='Perfis'