# Generated by Django 2.1.2 on 2018-10-05 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0109_bounty_funding_organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='bountyfulfillment',
            name='fulfiller_last_notified_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
