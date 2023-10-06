import string
import os
from django.conf import settings
from random import choice, shuffle
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO

def gerar_senha_aleatoria(tamanho):
    caracteres_especiais = string.punctuation
    caracteres = string.ascii_letters
    numeros_list = string.digits

    qtd = tamanho // 3
    sobra = 0

    if not tamanho % 3 == 0:
        sobra = tamanho - (qtd * 3)
    
    letras = ''
    for i in range(0, qtd + sobra):
        letras += choice(caracteres)

    numeros = ''
    for i in range(0, qtd):
        numeros += choice(numeros_list)
        
    especiais = ''
    for i in range(0, qtd):
        especiais += choice(caracteres_especiais)
        
    senha = list(letras + numeros + especiais)

    shuffle(senha)

    return ''.join(senha)



def gerar_pdf_exames(exame, paciente, senha):
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/senha_exame.html')
    context = {'exame': exame, 'paciente': paciente, 'senha': senha}
    template_render = render_to_string(path_template, context)

    path_output = BytesIO()

    #HTML(string=template_render).write_pdf(os.path.join(settings.BASE_DIR, 'templates/partial/senha_exame_teste.pdf'))
    HTML(string=template_render).write_pdf(path_output)
    path_output.seek(0)

    return path_output