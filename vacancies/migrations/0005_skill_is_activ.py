# Generated by Django 4.1.1 on 2022-09-30 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0004_alter_skill_options_alter_vacancy_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='is_activ',
            field=models.BooleanField(default=True),
        ),
    ]