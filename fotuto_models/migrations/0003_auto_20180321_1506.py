# Generated by Django 2.0.1 on 2018-03-21 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fotuto_models', '0002_auto_20180321_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='var',
            name='var_type',
            field=models.CharField(choices=[('food', 'Food'), ('voltaje', 'Voltaje'), ('presion', 'Presion')], default='voltaje', max_length=15),
        ),
    ]
