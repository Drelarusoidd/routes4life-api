# Generated by Django 4.0.3 on 2022-06-23 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routes4life_api', '0014_alter_category_places'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PlaceImages',
            new_name='PlaceImage',
        ),
    ]
