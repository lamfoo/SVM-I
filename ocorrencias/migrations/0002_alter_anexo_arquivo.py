# Generated by Django 5.0 on 2024-12-01 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexo',
            name='arquivo',
            field=models.FileField(upload_to='media'),
        ),
    ]