# Generated by Django 4.0.3 on 2022-07-12 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes4life_api', '0016_place_category_delete_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_premium',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
