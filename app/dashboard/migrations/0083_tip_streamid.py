# Generated by Django 2.2.4 on 2020-02-09 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0082_tip_stream'),
    ]

    operations = [
        migrations.AddField(
            model_name='tip',
            name='streamid',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
