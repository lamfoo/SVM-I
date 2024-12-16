from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LogsAPI, Estatisticas
import json

@receiver(post_save, sender=LogsAPI)
def atualizar_estatisticas(sender, instance, created, **kwargs):
    """Atualiza as estatísticas automaticamente quando um log é salvo."""
    if created:
        matricula = json.loads(instance.requisicao).get("matricula")
        if matricula:
            estatisticas, _ = Estatisticas.objects.get_or_create(
                matricula=matricula,
                usuario=instance.usuario
            )
            estatisticas.atualizar_estatisticas()
