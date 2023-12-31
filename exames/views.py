from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required
from . import models
from django.utils import timezone
from datetime import datetime


# Create your views here.
@login_required
def solicitar_exames(request):
    tipos_exames = models.TiposExames.objects.all()
    data_atual = timezone.now()
    if request.method == 'GET':        
        context = {'tipos_exames': tipos_exames}
        return render(request, 'solicitar_exames.html', context)
    elif request.method == 'POST':
        exames_id = request.POST.getlist('exames')
        solicitacao_exames = models.TiposExames.objects.filter(id__in=exames_id)
        preco_total = 0
        # TODO calcular preço dos dados disponíveis
        for i in solicitacao_exames:
            preco_total += i.preco
        context = {'tipos_exames': tipos_exames,
                    'preco_total': preco_total,
                    'solicitacao_exames': solicitacao_exames,
                    'data_atual': data_atual}
        return render(request, 'solicitar_exames.html', context)
    

@login_required
def fechar_pedido(request):
    exames_id = request.POST.getlist('exames')

    solicitacao_exames = models.TiposExames.objects.filter(id__in=exames_id)
    
    pedido_exame = models.PedidosExames(
        usuario=request.user,
        data=datetime.now()
    )
    pedido_exame.save()

    for exame in solicitacao_exames:
        solicitacao_exames_temp = models.SolicitacaoExame(
            usuario = request.user,
            exame=exame,
            status='E'            
        )
        solicitacao_exames_temp.save()
        pedido_exame.exames.add(solicitacao_exames_temp)
    pedido_exame.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido de exame realizado com sucesso')
    
    return redirect('gerenciar_pedidos')


@login_required
def gerenciar_pedidos(request):
    pedidos_exames = models.PedidosExames.objects.filter(usuario=request.user)
    context = {'pedidos_exames': pedidos_exames}
    return render(request, 'gerenciar_pedidos.html', context)


@login_required
def cancelar_pedido(request, pedido_id):
    pedido = models.PedidosExames.objects.get(id=pedido_id)
    
    if pedido.usuario == request.user:
        pedido.agendado = False
        pedido.save()
        messages.add_message(request, constants.SUCCESS, 'Pedido cancelado com sucesso')
    else:
        messages.add_message(request, constants.ERROR, "Usuário não autorizado a cancelar o pedido")
    return redirect('gerenciar_pedidos')


@login_required
def gerenciar_exames(request):
    exames = models.SolicitacaoExame.objects.filter(usuario=request.user)
    context = {'exames': exames}
    return render(request, 'gerenciar_exames.html', context)


@login_required
def permitir_abrir_exame(request, exame_id):
    exame = models.SolicitacaoExame.objects.get(id=exame_id)
    if not exame.requer_senha:
        try:
            return redirect(exame.resultado.url)
        except ValueError as e:
            messages.add_message(request, constants.ERROR, 'O exame não tem um arquivo PDF associado, contate um administrador')
            return redirect('gerenciar_exames')
    else:
        return redirect(f'/exames/solicitar_senha_exame/{exame_id}')
    

@login_required
def solicitar_senha_exame(request, exame_id):
    exame = models.SolicitacaoExame.objects.get(id=exame_id)
    if request.method == 'GET':        
        context = {'exame': exame}
        return render(request, 'solicitar_senha_exame.html', context)
    elif request.method == 'POST':
        senha = request.POST.get('senha')
        if exame.senha == senha:
            print('igual')
            return HttpResponse(exame.exame.nome)
        else:
            print('diferente')
            messages.add_message(request, constants.ERROR, "Senha incorreta")
            return redirect(f'/exames/solicitar_senha_exame/{exame_id}')
        

@login_required
def gerar_acesso_medico(request):
    if request.method == "GET":
        acessos_medicos = models.AcessoMedico.objects.filter(usuario =request. user)
        return render(request, 'gerar_acesso_medico.html', {'acessos_medicos': acessos_medicos})
    elif request.method == "POST":
        identificacao = request.POST.get('identificacao')
        tempo_de_acesso = request.POST.get('tempo_de_acesso')
        data_exame_inicial = request.POST.get("data_exame_inicial")
        data_exame_final = request.POST.get("data_exame_final")

        acesso_medico = models.AcessoMedico(
            usuario = request.user,
            identificacao = identificacao,
            tempo_de_acesso = tempo_de_acesso,
            data_exames_iniciais = data_exame_inicial,
            data_exames_finais = data_exame_final,
            criado_em = datetime.now()
        )

        acesso_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Acesso gerado com sucesso')
        return redirect('/exames/gerar_acesso_medico')
    

def acesso_medico(request, token):
    acesso_medico = models.AcessoMedico.objects.get(token=token)
    if acesso_medico.status == 'Expirado':
        messages.add_message(request, constants.ERROR, "Link expirado, solicite um novo acesso")
        return redirect('/usuarios/login')
    else:
        pedidos = models.PedidosExames.objects.filter(usuario=acesso_medico.usuario).\
        filter(data__gte=acesso_medico.data_exames_iniciais).\
        filter(data__lte=acesso_medico.data_exames_finais)
        context = {'pedidos': pedidos}
        return render(request, 'acesso_medico.html', context)
