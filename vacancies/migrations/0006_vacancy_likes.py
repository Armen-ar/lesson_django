# Generated by Django 4.1.1 on 2022-10-06 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0005_skill_is_activ'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]