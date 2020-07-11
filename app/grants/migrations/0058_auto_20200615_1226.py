# Generated by Django 2.2.4 on 2020-06-15 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0057_auto_20200527_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grant',
            name='grant_type',
            field=models.CharField(choices=[('tech', 'tech'), ('health', 'health'), ('Community', 'media'), ('Crypto for Black Lives', 'change'), ('matic', 'matic')], default='tech', help_text='Grant CLR category', max_length=15),
        ),
    ]
