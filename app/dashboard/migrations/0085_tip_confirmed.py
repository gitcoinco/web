# Generated by Django 2.2.4 on 2020-03-03 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0084_auto_20200227_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='tip',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
