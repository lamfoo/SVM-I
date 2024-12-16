from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
import requests

class Pesquisar(models.Model):
    matricula = models.CharField(max_length=50, verbose_name="Matrícula")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pesquisas", verbose_name="Usuário", blank=True, null=True)

    class Meta:
        verbose_name = "Pesquisa"
        verbose_name_plural = "Inspeções"

    def buscar_dados(self):
        """Lógica para consultar a API com a matrícula, com suporte a cache e tratamento de exceções."""
        cache_key = f"pesquisa_{self.matricula}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        url = f"https://foopython.pythonanywhere.com/api/v1/inspections//?eq(matricula,{self.matricula})"
        try:
            response = requests.get(url, timeout=5)  # Timeout para evitar travamentos
            response.raise_for_status()  # Levanta exceção para códigos HTTP de erro
            data = response.json()  # Supondo que retorna JSON
            cache.set(cache_key, data, timeout=3600)  # Cache por 1 hora
            return data
        except requests.exceptions.RequestException as e:
            # Log de erro (opcional)
            print(f"Erro ao acessar a API: {e}")
            return [{"erro": "serviço indisponível"}]  # Resultado padrão para erro

    def __str__(self):
        return f"Pesquisa: {self.matricula} - {self.usuario}"


class PesquisarV2(models.Model):
    matricula = models.CharField(max_length=50, verbose_name="Matrícula")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pesquisas_v2", verbose_name="Usuário", blank=True, null=True)

    class Meta:
        verbose_name = "Pesquisa"
        verbose_name_plural = "Matriculas"

    def buscar_dados(self):
        """Lógica para consultar a API com a matrícula, com suporte a cache e tratamento de exceções."""
        cache_key = f"pesquisa_v2_{self.matricula}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # URL corrigida para v2 da API
        url = f"https://foopython.pythonanywhere.com/api/v2/plate-registrations/?eq(matricula,{self.matricula})"
        try:
            response = requests.get(url, timeout=5)  # Timeout para evitar travamentos
            response.raise_for_status()  # Levanta exceção para códigos HTTP de erro
            data = response.json()  # Supondo que retorna JSON
            cache.set(cache_key, data, timeout=3600)  # Cache por 1 hora
            return data
        except requests.exceptions.RequestException as e:
            # Log de erro (opcional)
            print(f"Erro ao acessar a API: {e}")
            return [{"erro": "serviço indisponível"}]  # Resultado padrão para erro

    def __str__(self):
        return f"Pesquisa V2: {self.matricula} - {self.usuario}"