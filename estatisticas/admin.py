from django.contrib import admin
from .models import Estatisticas

@admin.register(Estatisticas)
class EstatisticasAdmin(admin.ModelAdmin):
    list_display = (
        'matricula', 
        'total_verificacoes', 
        'total_inspecoes_invalidas', 
        'verificacoes_matricula_invalida', 
        'data_relatorio', 
        'usuario_id'
    )
    list_filter = ('data_relatorio',)  # Filtro por data
    search_fields = ('matricula',)    # Campo de busca por matrícula
    readonly_fields = (
        'total_verificacoes', 
        'total_inspecoes_invalidas', 
        'verificacoes_matricula_invalida', 
        'data_relatorio'
    )  # Campos que não podem ser editados no admin
    ordering = ('-data_relatorio',)   # Ordenar do mais recente ao mais antigo

    def get_queryset(self, request):
        """
        Sobrescreve o queryset para permitir que apenas administradores 
        vejam todas as estatísticas.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtrar apenas as estatísticas relacionadas ao usuário
        return qs.filter(usuario_id=request.user.id)
