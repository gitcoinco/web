# Generated by Django 2.2.4 on 2020-06-18 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0061_auto_20200617_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='is_clr_eligible',
            field=models.BooleanField(default=True, help_text='Is grant eligible for CLR'),
        ),
    ]
