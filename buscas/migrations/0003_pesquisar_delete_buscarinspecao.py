# Generated by Django 5.0 on 2024-12-01 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buscas', '0002_buscarinspecao_delete_pesquisar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pesquisar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=50, verbose_name='Matrícula')),
            ],
            options={
                'verbose_name': 'Pesquisa',
                'verbose_name_plural': 'Pesquisas',
            },
        ),
        migrations.DeleteModel(
            name='BuscarInspecao',
        ),
    ]