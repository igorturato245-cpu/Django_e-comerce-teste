from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class Perfiladmin(admin.ModelAdmin):
    pass