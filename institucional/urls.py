from django.urls import path
from institucional import views

app_name = 'institucional'

urlpatterns = [
    path('sobre-nos/',views.SobreNos.as_view(),name='sobre'),
    path('contato/',views.Contato.as_view(),name='contato'),
    path('termo-de-uso/',views.TermoDeUso.as_view(),name='termo-uso'),
    path('politica-de-privacidade/',views.PoliticaDePrivacidade.as_view(),name='politica-privacidade'),
    path('politica-de-troca/',views.PoliticaDeTroca.as_view(),name='politica-troca'),
]
