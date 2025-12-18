from django.urls import path
from cadastro_de_usuarios.views import view_usuario

app_name="cadastro_login"

urlpatterns = [
    path('' , view_usuario.cadastro , name='cadastro'),
    path('login/', view_usuario.login_view, name='loginuser'),
    path('atualizar_cadastro/',view_usuario.atualizacaodecadastro,name='atualizarcadastro'),
    path('logout/',view_usuario.logout,name='logoutuser'),
]
