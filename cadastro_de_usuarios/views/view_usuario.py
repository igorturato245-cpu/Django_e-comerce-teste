from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm

from cadastro_de_usuarios.forms import Cadastraruser,Atualizarcadastro


def cadastro(request):
    form = Cadastraruser(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário cadastrado com sucesso")
            return redirect('e_comerce:index')

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
            return redirect('e_comerce:index')
        messages.error(request,'Login inválido')

    context={'form':form}

    return render(
        request,
        'cadastro_de_usuarios/login.html',
        context
    )

@login_required(login_url='cadastro_login/loginuser')
def logout(request):
    auth.logout(request)
    return redirect('cadastro_login:loginuser')