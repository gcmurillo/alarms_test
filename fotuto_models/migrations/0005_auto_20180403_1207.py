# Generated by Django 2.0.3 on 2018-04-03 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fotuto_models', '0004_auto_20180322_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_type', models.CharField(choices=[('AL', 'Alimentador'), ('AR', 'Airador'), ('RP', 'Repetidora')], default='AL', max_length=20)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(blank=True, max_length=80)),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fotuto_models.Profile'),
        ),
    ]
