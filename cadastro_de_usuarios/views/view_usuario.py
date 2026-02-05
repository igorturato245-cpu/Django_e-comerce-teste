from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import auth
from cadastro_de_usuarios import models,forms
import copy
from django.contrib import messages


class BasePerfil(View):
    template_name='cadastro_de_usuarios/cadastro.html'
    
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
    
        self.carrinho=copy.deepcopy(self.request.session.get('carrinho',{}))
        
        self.perfil=None
        
        if self.request.user.is_authenticated:
            self.perfil=models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()
            
            self.contexto={
                'form_cadastro':forms.CadastroForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user
                ),
                'perfil_cadastro':forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
            
        else:
            self.contexto={
                'form_cadastro':forms.CadastroForm(
                    data=self.request.POST or None
                ),
                'perfil_cadastro':forms.PerfilForm(
                    data=self.request.POST or None
                )
            }
            
        self.form_cadastro=self.contexto['form_cadastro']
        self.perfil_form=self.contexto['perfil_cadastro']
        
        if self.request.user.is_authenticated:
            self.template_name='cadastro_de_usuarios/user_update.html'
            
        self.renderizar=render(self.request,self.template_name,self.contexto)
        
    def get(self,*args, **kwargs):
        return self.renderizar
    
    
class CriarUser(BasePerfil):
    def post(self,*args, **kwargs):
        if not self.form_cadastro.is_valid() or not self.perfil_form.is_valid():
            return self.renderizar
        
        password=self.form_cadastro.cleaned_data.get('password')
        
        usuario=self.form_cadastro.save(commit=False)
        usuario.set_password(password)
        usuario.save()
        
        perfil=self.perfil_form.save(commit=False)
        perfil.usuario=usuario
        perfil.save()
        
        if password:
            autentica=authenticate(
                self.request,
                username=usuario,
                password=password,
            )
            if autentica:
                login(self.request,user=usuario)
                
        self.request.session['carrinho']=self.carrinho
        self.request.session.save()
        
        messages.success(self.request,'Sucesso ao criar sua conta, boas compras.')
        
        return redirect('cadastro_login:atualizarcadastro')
    
class AtualizarUser(BasePerfil):
    def post(self,*args, **kwargs):
        if not self.form_cadastro.is_valid() or not self.perfil_form.is_valid():
            return self.renderizar
        
        username=self.form_cadastro.cleaned_data.get('username')
        password=self.form_cadastro.cleaned_data.get('password')
        email=self.form_cadastro.cleaned_data.get('email')
        first_name=self.form_cadastro.cleaned_data.get('first_name')
        last_name=self.form_cadastro.cleaned_data.get('last_name')
        
        if self.request.user.is_authenticated:
            usuario=get_object_or_404(
                User,pk=self.request.user.pk
            )
            usuario.username=username
            
            if password:
                usuario.set_password(password)
                
            usuario.email=email
            usuario.first_name=first_name
            usuario.last_name=last_name
            usuario.save()
            self.request.user=usuario
            
            if not self.perfil:
                self.perfil_form.cleaned_data['usuario']=usuario
                perfil=models.Perfil(**self.form_cadastro.cleaned_data)
                perfil.save()
                
            else:
                perfil=self.perfil_form.save(commit=False)
                perfil.usuario=usuario
                perfil.save()
                
        if password:
            autentica=authenticate(
                self.request,
                username=usuario,
                password=password
            )
            if autentica:
                login(self.request,user=usuario)
                
        self.request.session['carrinho']=self.carrinho
        self.request.session.save()
        
        messages.success(self.request,'Sucesso ao atualizar dados de usuario.')
        
        return redirect('produtos:index')
    
class loginviw(View):
    def get(self,request):
        form=AuthenticationForm()
        return render(
            request,'cadastro_de_usuarios/login.html',{'form_cadastro':form}
        ) 
    def post(self,request):
        carrinho_anonimo=copy.deepcopy(self.request.session.get('carrinho',{}))
        
        form=AuthenticationForm(self.request,data=self.request.POST)
        
        if form.is_valid():
            user=form.get_user()
            auth.login(request,user)
            self.request.session['carrinho']=carrinho_anonimo
            self.request.session.modified=True
            self.request.session.save()
            messages.success(request,'Sucesso ao fazer login.')
            return redirect('carrinho:carrinho')
        
        messages.error(
                request,'Erro ao autentificar usuario'
            )
        
        return redirect('produtos:index')
    
class logoutviw(View):
    def get(self,*args, **kwargs):
        carrinho=copy.deepcopy(self.request.session.get('carrinho',{}))
        logout(self.request)
        self.request.session['carrinho']=carrinho
        self.request.session.modified=True
        self.request.session.save()
        return redirect('produtos:index')