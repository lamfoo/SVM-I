import json  # Certifique-se de importar o módulo json
from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
import requests

class LogsAPI(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome_api = models.CharField(
        max_length=255, 
        null=False, 
        help_text="Nome ou URL da API utilizada."
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="logs_api", 
        help_text="Usuário que realizou a requisição."
    )
    requisicao = models.TextField(
        null=False, 
        help_text="Dados enviados para a pesquisa (parâmetros da requisição)."
    )
    resposta = models.TextField(
        null=False, 
        help_text="Dados retornados pela API."
    )
    data_hora = models.DateTimeField(
        auto_now_add=True, 
        help_text="Data e hora da requisição."
    )

    class Meta:
        verbose_name = "Log de API"
        verbose_name_plural = "Logs de API"
        ordering = ["-data_hora"]  # Logs mais recentes aparecem primeiro

    def __str__(self):
        return f"{self.nome_api} - {self.usuario.username} em {self.data_hora}"

    def salvar_log(self, nome_api, usuario, dados_requisicao, dados_resposta):
        """Método para salvar os dados de uma requisição à API no banco."""
        self.nome_api = nome_api
        self.usuario = usuario
        self.requisicao = json.dumps(dados_requisicao)  # Salvando os dados enviados
        self.resposta = json.dumps(dados_resposta)  # Salvando os dados retornados
        self.save()

    def buscar_dados_api(self, url, parametros):
        """Método que consulta a API e salva os logs da requisição."""
        cache_key = f"api_request_{url}_{json.dumps(parametros)}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data

        try:
            response = requests.get(url, params=parametros, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Salvando log no banco de dados
            self.salvar_log(nome_api=url, usuario=self.usuario, dados_requisicao=parametros, dados_resposta=data)

            # Cache da resposta por 1 hora
            cache.set(cache_key, data, timeout=3600)
            return data

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a API: {e}")
            return {"erro": "serviço indisponível"}
