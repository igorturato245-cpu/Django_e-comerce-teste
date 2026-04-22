from django.contrib import admin
from .models import Perfil,Endereco

@admin.register(Perfil)
class Perfiladmin(admin.ModelAdmin):
    pass

@admin.register(Endereco)
class Enderecoadmin(admin.ModelAdmin):
    pass