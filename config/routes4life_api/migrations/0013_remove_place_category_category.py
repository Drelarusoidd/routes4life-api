# Generated by Django 4.0.3 on 2022-06-23 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes4life_api', '0012_alter_place_added_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='category',
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('places', models.ManyToManyField(related_name='categories', to='routes4life_api.place')),
            ],
        ),
    ]
