# Generated by Django 2.2.4 on 2020-10-09 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0158_profile_is_idena_connected'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='idena_nonce',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
