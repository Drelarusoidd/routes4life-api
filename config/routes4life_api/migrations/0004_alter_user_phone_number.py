# Generated by Django 4.0.3 on 2022-04-19 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes4life_api', '0003_alter_user_options_user_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default='+000000000', max_length=16, verbose_name='phone number'),
        ),
    ]
