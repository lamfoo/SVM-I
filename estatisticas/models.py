from django.db import models
from django.contrib.auth.models import User
from logsapi.models import LogsAPI  # Certifique-se de usar o caminho corretoimport json

class Estatisticas(models.Model):
    id = models.BigAutoField(primary_key=True)
    matricula = models.CharField(max_length=20)
    total_verificacoes = models.IntegerField(default=0)
    total_inspecoes_invalidas = models.IntegerField(default=0)
    verificacoes_matricula_invalida = models.IntegerField(default=0)
    data_relatorio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Estatisticas'
        verbose_name = 'Estatística'
        verbose_name_plural = 'Estatísticas'

    def __str__(self):
        return f"Estatísticas para {self.matricula}"

    def atualizar_estatisticas(self):
        """Atualiza os campos do modelo com base nos dados de LogsAPI."""
        logs = LogsAPI.objects.filter(
            requisicao__icontains=self.matricula, usuario=self.usuario
        )
        
        self.total_verificacoes = logs.count()

        # Filtrar logs relacionados à API de inspeções
        logs_inspections = logs.filter(nome_api__icontains="inspections")
        self.total_inspecoes_invalidas = logs_inspections.filter(
            resposta__icontains="Nenhum resultado encontrado"
        ).count()

        # Filtrar logs relacionados à API de registros de placas
        logs_plate_registrations = logs.filter(nome_api__icontains="plate-registrations")
        self.verificacoes_matricula_invalida = logs_plate_registrations.filter(
            resposta__icontains="Nenhum resultado encontrado"
        ).count()

        self.save()
