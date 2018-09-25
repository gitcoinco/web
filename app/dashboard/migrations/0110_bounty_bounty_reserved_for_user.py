# Generated by Django 2.1.1 on 2018-09-25 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0109_bounty_funding_organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='bounty_reserved_for_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reserved_bounties', to='dashboard.Profile'),
        ),
    ]
