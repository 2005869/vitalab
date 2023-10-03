from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    try:
        first_name = request.POST.get('primeiro_nome')
        last_name = request.POST.get('ultimo_nome')
        username = request.POST.get('username')
        password = request.POST.get('senha')
        password2 = request.POST.get('confirmar_senha')
        email = request.POST.get('email')

        if len(password) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir 7 ou mais digitos')
            return redirect('cadastro')

        if not password == password2:
            messages.add_message(request, constants.ERROR, 'As senhas não são iguais')
            return redirect('cadastro')

        # TODO validar username único
        if request.method == 'POST':
        
            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                password = password,
                email = email,            
            )
            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso')
            return HttpResponse('OK')
    except:
        messages.add_message(request, constants.ERROR, 'Erro interno do sistema, contate um administrador')
        redirect('cadastro')


def logar(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)
        
        if user:
            login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Login efetuado com sucesso')
            return redirect('/')
        else:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('login')