from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Ocorrencia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_relatorio = models.CharField(max_length=100)
    descricao = models.TextField()  # Campo de descrição
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ocorrência de {self.usuario.username}"

class Anexo(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, related_name='anexos', on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='media')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anexo de {self.ocorrencia.tipo_relatorio} - {self.id}"
