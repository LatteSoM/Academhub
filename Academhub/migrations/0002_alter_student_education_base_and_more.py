# Generated by Django 4.2.18 on 2025-01-29 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Academhub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='education_base',
            field=models.CharField(choices=[('9 класс', '9'), ('11 класс', '11')], max_length=255, verbose_name='База образования'),
        ),
        migrations.AlterField(
            model_name='student',
            name='education_basis',
            field=models.CharField(choices=[('Бюджеьная основа', 'Бюджет'), ('Внебюджетная основа', 'Внебюджет')], max_length=255, verbose_name='Основа образования'),
        ),
    ]
