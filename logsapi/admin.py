import requests
import json
from django.contrib import admin
from .models import LogsAPI
from buscas.models import Pesquisar, PesquisarV2
from django.utils.html import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver

@admin.register(LogsAPI)
class LogsAPIAdmin(admin.ModelAdmin):
    list_display = ('nome_api', 'usuario', 'data_hora', 'visualizar_dados')
    search_fields = ('nome_api', 'usuario__username')
    list_filter = ['nome_api', 'usuario']
    list_per_page = 10

    def visualizar_dados(self, obj):
        """Exibe uma pré-visualização dos dados armazenados no log."""
        dados_requisicao = json.loads(obj.requisicao)
        dados_resposta = json.loads(obj.resposta)
        return mark_safe(f"<pre>{json.dumps(dados_requisicao, indent=2)}</pre> <hr> <pre>{json.dumps(dados_resposta, indent=2)}</pre>")
    
    visualizar_dados.short_description = "Visualizar Dados"

# Conectar o sinal que irá criar um log sempre que uma pesquisa for salva (API 1)
@receiver(post_save, sender=Pesquisar)
def criar_log_api(sender, instance, created, **kwargs):
    """Sinal para criar um log no modelo LogsAPI após uma pesquisa ser salva (API 1)."""
    if created:
        url = f"https://foopython.pythonanywhere.com/api/v1/inspections//?eq(matricula,{instance.matricula})"
        parametros = {"matricula": instance.matricula}
        
        try:
            response = requests.get(url, params=parametros, timeout=5)
            response.raise_for_status()
            dados_resposta = response.json()

            if dados_resposta:
                dados_formatados = {
                    "matricula": dados_resposta[0].get("matricula"),
                    "modelo": dados_resposta[0].get("modelo"),
                    "marca": dados_resposta[0].get("marca"),
                    "n_quadro": dados_resposta[0].get("n_quadro"),
                    "n_motor": dados_resposta[0].get("n_motor"),
                    "ano": dados_resposta[0].get("ano"),
                    "data_criacao_inspecao": dados_resposta[0].get("data_criacao_inspecao"),
                    "data_proxima_inspecao": dados_resposta[0].get("data_proxima_inspecao"),
                    "n_ficha": dados_resposta[0].get("n_ficha"),
                }

                LogsAPI.objects.create(
                    nome_api=url,
                    usuario=instance.usuario,
                    requisicao=json.dumps(parametros),
                    resposta=json.dumps(dados_formatados)
                )
            else:
                # Caso não existam dados na resposta
                LogsAPI.objects.create(
                    nome_api=url,
                    usuario=instance.usuario,
                    requisicao=json.dumps(parametros),
                    resposta=json.dumps({"mensagem": "Nenhum resultado encontrado"})
                )
        except requests.exceptions.RequestException as e:
            LogsAPI.objects.create(
                nome_api=url,
                usuario=instance.usuario,
                requisicao=json.dumps(parametros),
                resposta=json.dumps({"erro": str(e)})
            )


# Conectar o sinal que irá criar um log sempre que uma pesquisa v2 for salva (API 2)
@receiver(post_save, sender=PesquisarV2)
def criar_log_api_v2(sender, instance, created, **kwargs):
    """Sinal para criar um log no modelo LogsAPI após uma pesquisa v2 ser salva (API 2)."""
    if created:
        url = f"https://foopython.pythonanywhere.com/api/v2/plate-registrations/?eq(matricula,{instance.matricula})"
        parametros = {"matricula": instance.matricula}
        
        try:
            response = requests.get(url, params=parametros, timeout=5)
            response.raise_for_status()
            dados_resposta = response.json()

            if dados_resposta:
                dados_formatados = {
                "matricula": dados_resposta[0].get("matricula"),
                "marca": dados_resposta[0].get("marca"),
                "modelo": dados_resposta[0].get("modelo"),
                "ano_fabricacao": dados_resposta[0].get("ano_fabricacao"),
                "cor": dados_resposta[0].get("cor"),
                "tipo_veiculo": dados_resposta[0].get("tipo_veiculo"),
                "categoria": dados_resposta[0].get("categoria"),
                "numero_motor": dados_resposta[0].get("numero_motor"),
                "numero_quadro": dados_resposta[0].get("numero_quadro"),
                "nome_proprietario": dados_resposta[0].get("nome_proprietario"),
                "endereco_rua": dados_resposta[0].get("endereco_rua"),
                "endereco_numero": dados_resposta[0].get("endereco_numero"),
                "endereco_bairro": dados_resposta[0].get("endereco_bairro"),
                "endereco_cidade": dados_resposta[0].get("endereco_cidade"),
                "endereco_provincia": dados_resposta[0].get("endereco_provincia"),
                "endereco_codigo_postal": dados_resposta[0].get("endereco_codigo_postal"),
                "data_emissao": dados_resposta[0].get("data_emissao"),
                "numero_registro": dados_resposta[0].get("numero_registro"),
                "local_registro": dados_resposta[0].get("local_registro"),
                "documento_identidade": dados_resposta[0].get("documento_identidade"),
            }
                
                LogsAPI.objects.create(
                    nome_api=url,
                    usuario=instance.usuario,
                    requisicao=json.dumps(parametros),
                    resposta=json.dumps(dados_formatados)
                )
            else:
                # Caso não existam dados na resposta
                LogsAPI.objects.create(
                    nome_api=url,
                    usuario=instance.usuario,
                    requisicao=json.dumps(parametros),
                    resposta=json.dumps({"mensagem": "Nenhum resultado encontrado"})
                )
        except requests.exceptions.RequestException as e:
            LogsAPI.objects.create(
                nome_api=url,
                usuario=instance.usuario,
                requisicao=json.dumps(parametros),
                resposta=json.dumps({"erro": str(e)})
            )
