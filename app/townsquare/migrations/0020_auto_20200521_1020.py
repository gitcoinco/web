# Generated by Django 2.2.4 on 2020-05-21 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('townsquare', '0019_pinnedpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pinnedpost',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pin', to='dashboard.Activity'),
        ),
    ]
