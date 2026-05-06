from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Contato_user
from django.contrib import messages
from django.shortcuts import redirect

class SobreNos(TemplateView):
    template_name = 'institucional/sobre.html'
    
class Contato(TemplateView):
    template_name = 'institucional/contato.html'
     
    def get(self,request):
        return render(request, self.template_name)
    
    def post(self,request):
        nome=request.POST.get('Nome')
        email=request.POST.get('Email')
        texto=request.POST.get('Área de contato')
        
        
        Contato_user.objects.update_or_create(
            nome=nome,
            email=email,
            texto=texto
        )
        
        messages.success(request,'Sucesso ao entrar em contato com nosso time, logo mais retornamos nossa resposta.')
        return redirect('produtos:index')
        

class TermoDeUso(TemplateView):
    template_name = 'institucional/termo-uso.html'
    
class PoliticaDePrivacidade(TemplateView):
    template_name = 'institucional/politica-privacidade.html'
    
class PoliticaDeTroca(TemplateView):
    template_name = 'institucional/politica-troca.html'