# Generated by Django 5.0.3 on 2024-04-30 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
