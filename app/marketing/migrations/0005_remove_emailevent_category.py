# Generated by Django 2.1.7 on 2019-04-06 02:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0004_auto_20190406_0156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailevent',
            name='category',
        ),
    ]
