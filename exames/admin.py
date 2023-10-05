from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.TiposExames)
admin.site.register(models.PedidosExames)
admin.site.register(models.SolicitacaoExame)