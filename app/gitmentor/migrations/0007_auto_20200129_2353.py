# Generated by Django 2.2.4 on 2020-01-29 23:53

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitmentor', '0006_auto_20200128_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionrequest',
            name='sablier_stream_id',
            field=models.CharField(blank=True, db_index=True, max_length=50),
        ),
        migrations.AddField(
            model_name='sessionrequest',
            name='sablier_tx_receipt',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='sessionrequest',
            name='session_datetime',
            field=models.CharField(blank=True, help_text='Requested session date and time.', max_length=256),
        ),
    ]
