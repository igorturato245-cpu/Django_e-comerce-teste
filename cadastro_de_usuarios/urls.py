from django.urls import path
from cadastro_de_usuarios.views import view_usuario

app_name="cadastro_login"

urlpatterns = [
    path('' , view_usuario.CriarUser.as_view() , name='cadastro'),
    path('login/', view_usuario.loginviw.as_view(), name='loginuser'),
    path('atualizar_cadastro/',view_usuario.AtualizarUser.as_view(),name='atualizarcadastro'),
    path('logout/',view_usuario.logoutviw.as_view(),name='logoutuser'),
]
