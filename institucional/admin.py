from django.contrib import admin
from .models import Contato_user

@admin.register(Contato_user)
class Contato_user_admin(admin.ModelAdmin):
    pass