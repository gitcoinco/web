# Generated by Django 2.2.4 on 2020-10-08 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0153_hackathonevent_use_circle'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='idena_address',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
