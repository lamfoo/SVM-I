from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
import csv
from .models import Ocorrencia, Anexo


class UsuarioFilter(admin.SimpleListFilter):
    title = _('Usuário')
    parameter_name = 'usuario'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            usuarios = model_admin.get_queryset(request).values_list('usuario__id', 'usuario__username').distinct()
            return [(usuario[0], usuario[1]) for usuario in usuarios]
        return [(request.user.id, request.user.username)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(usuario_id=self.value())
        return queryset


class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 1


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_relatorio', 'descricao', 'data_criacao', 'mostrar_anexos')
    search_fields = ('usuario__username', 'tipo_relatorio')
    list_filter = (UsuarioFilter, 'tipo_relatorio')
    inlines = [AnexoInline]
    actions = ['export_to_csv']

    def mostrar_anexos(self, obj):
        anexos = obj.anexos.all()
        if anexos:
            anexos_html = []
            for anexo in anexos:
                if anexo.arquivo.name.endswith(('jpg', 'jpeg', 'png', 'gif')):
                    anexos_html.append(
                        format_html('<a href="{url}" target="_blank"><img src="{url}" width="30" height="30" /></a>',
                                    url=anexo.arquivo.url)
                    )
                else:
                    anexos_html.append(
                        format_html('<a href="{url}" target="_blank">{filename}</a>',
                                    url=anexo.arquivo.url,
                                    filename=anexo.arquivo.name)
                    )
            return format_html(' | '.join(anexos_html))
        return "Nenhum anexo"

    mostrar_anexos.short_description = 'Anexos'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            if 'usuario' in form.base_fields:
                form.base_fields['usuario'].disabled = True
                form.base_fields['usuario'].initial = request.user
        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ocorrencias.csv"'
        writer = csv.writer(response)
        writer.writerow(['Usuário', 'Tipo de Relatório', 'Data Criação', 'Anexo'])
        for ocorrencia in queryset:
            writer.writerow([
                ocorrencia.usuario.username,
                ocorrencia.tipo_relatorio,
                ocorrencia.data_criacao,
                ', '.join([str(anexo.arquivo) for anexo in ocorrencia.anexos.all()])
            ])
        return response

    export_to_csv.short_description = 'Exportar para CSV'


@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ('ocorrencia', 'arquivo', 'data_upload')

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
