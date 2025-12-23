from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from cadastro_de_usuarios.forms import Cadastraruser,Atualizarcadastro


# Certifique-se de importar o User no topo do arquivo
from django.contrib.auth.models import User 
from django.contrib import messages
from django.shortcuts import render, redirect

def cadastro(request):
    form = Cadastraruser(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            # --- CORREÇÃO DO ERRO (IntegrityError) ---
            # 1. Pega os dados que o usuário digitou (limpos pelo Django)
            username_digitado = form.cleaned_data.get('username')
            email_digitado = form.cleaned_data.get('email')

            # 2. Verifica manualmente se o usuário já existe no banco
            if User.objects.filter(username=username_digitado).exists():
                messages.error(request, "Este nome de usuário já está em uso. Escolha outro.")
                # Interrompe e volta para a tela de cadastro
                return render(request, 'cadastro_de_usuarios/cadastro.html', {'form': form})

            # (Opcional) Verifica se o e-mail já existe
            if email_digitado and User.objects.filter(email=email_digitado).exists():
                messages.error(request, "Este e-mail já possui cadastro.")
                return render(request, 'cadastro_de_usuarios/cadastro.html', {'form': form})

            # --- SALVAR ---
            # Se passou pelas verificações acima, pode salvar sem medo de erro 500
            user = form.save()
            
            # --- LOGIN AUTOMÁTICO (Sugestão) ---
            # Geralmente quando a pessoa cadastra, já queremos logar ela.
            # Se quiser isso, precisaria importar 'login' do django.contrib.auth e fazer:
            # login(request, user) 

            messages.success(request, "Usuário cadastrado com sucesso")

            # --- REDIRECIONAMENTO INTELIGENTE (Next) ---
            # Verifica se tem um destino (ex: carrinho) na URL
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Se não tiver destino específico, vai para a home (ou login)
            return redirect('produtos:index') 

    return render(
        request,
        'cadastro_de_usuarios/cadastro.html',
        {'form': form}
    )

    
@login_required(login_url='cadastro_login:loginuser')    
def atualizacaodecadastro(request):
    form=Atualizarcadastro(instance=request.user)

    context={'form':form,}

    if request.method != 'POST':
        return render(
            request,
            'cadastro_de_usuarios/user_update.html',
            context
        )
    
    form=Atualizarcadastro(data=request.POST,instance=request.user)

    if not form.is_valid():
        return render(
            request,
            'cadastro_de_usuarios/user_update.html',
            context
        )

    form.save()
    return redirect('cadastro_login:atualizarcadastro')

def login_view(request):
    form=AuthenticationForm(request)

    if request.method == 'POST':
        form= AuthenticationForm(request,data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth.login(request,user)
            messages.success(request,'Logado com sucesso!')
            return redirect('produtos:index')
        messages.error(request,'Login inválido')

    context={'form':form}

    return render(
        request,
        'cadastro_de_usuarios/login.html',
        context
    )

def logout(request):
    auth.logout(request)
    return redirect('produtos:index')