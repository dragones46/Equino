# Generated by Django 4.2.6 on 2025-01-30 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concentrado_equino', '0003_alter_usuario_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='precio',
            field=models.IntegerField(),
        ),
    ]
