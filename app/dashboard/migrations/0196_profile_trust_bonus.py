# Generated by Django 2.2.24 on 2021-11-16 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0195_auto_20211116_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='trust_bonus',
            field=models.DecimalField(decimal_places=2, default=0.5, help_text='Trust Bonus score based on verified services', max_digits=5),
        ),
    ]
