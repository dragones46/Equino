# Generated by Django 4.2.6 on 2025-03-06 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concentrado_equino', '0005_alter_pago_qr_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pago',
            name='qr_codigo',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
    ]
