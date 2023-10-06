from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.contrib.auth.models import User
from django.db.models.functions import Concat
from django.db.models import Value
from django.contrib.admin.views.decorators import staff_member_required
from exames import models as examesModels
from . import utils
from django.contrib import messages
from django.contrib.messages import constants


# Create your views here.
@staff_member_required
def gerenciar_clientes(request):
    clientes = User.objects.filter(is_staff=False)

    nome_completo = request.GET.get('nome')
    email = request.GET.get('email')

    if email:
        clientes = clientes.filter(email__contains=email)

    if nome_completo:
        clientes = clientes.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).\
        filter(full_name__contains=nome_completo)

    context = {'clientes': clientes}
    return render(request, 'gerenciar_clientes.html', context)


@staff_member_required 
def cliente(request, cliente_id):
    cliente = User.objects.get(id=cliente_id)
    exames = examesModels.SolicitacaoExame.objects.filter(usuario=cliente)
    return render(request, 'cliente.html', {'cliente': cliente, 'exames': exames})


@staff_member_required
def exame_cliente(request, exame_id):
    exame = examesModels.SolicitacaoExame.objects.get(id=exame_id)
    context = {'exame': exame}
    return render(request, 'exame_cliente.html', context)


def proxy_pdf(request, exame_id):
    exame = examesModels.SolicitacaoExame.objects.get(id=exame_id)
    try:
        response = exame.resultado.open()
        return HttpResponse(response)
    except ValueError as e:
        return redirect('gerenciar_clientes')
    

def gerar_senha(request, exame_id):
    exame = examesModels.SolicitacaoExame.objects.get(id=exame_id)

    if exame.senha:
        return FileResponse(utils.gerar_pdf_exames(exame.exame.nome, exame.usuario.first_name, exame.senha), filename='token.pdf')
    
    senha = utils.gerar_senha_aleatoria(6)
    exame.senha = senha
    exame.requer_senha = True
    exame.save()
    return FileResponse(utils.gerar_pdf_exames(exame.exame, exame.usuario.first_name, exame.senha), filename='token.pdf')


def alterar_dados_exame(request, exame_id):
    exame = examesModels.SolicitacaoExame.objects.get(id=exame_id)

    pdf = request.FILES.get('resultado')
    status = request.POST.get('status')
    requer_senha = request.POST.get('requer_senha')

    if requer_senha and (not exame.senha):
        messages.add_message(request, constants.ERROR, 'Para exigir a senha primeiro crie uma senha')
        return redirect(f'/empresarial/exame_cliente/{exame.id}')
    exame.requer_senha = True if requer_senha else False

    if pdf:
        exame.resultado = pdf
    exame.status = status
    exame.save()
    messages.add_message(request, constants.SUCCESS, 'Dados alterados com sucesso')
    return redirect(f'/empresarial/exame_cliente/{exame.id}')