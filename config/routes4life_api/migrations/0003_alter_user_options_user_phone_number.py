# Generated by Django 4.0.2 on 2022-02-21 13:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes4life_api', '0002_alter_user_managers_remove_user_username'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default='80291506285', max_length=16, validators=[django.core.validators.RegexValidator('^[+]?[0-9]{7,15}$', 'Invalid phone number.')], verbose_name='phone number'),
            preserve_default=False,
        ),
    ]
