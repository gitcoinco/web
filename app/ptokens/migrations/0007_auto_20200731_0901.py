# Generated by Django 2.2.4 on 2020-07-31 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0125_auto_20200724_1050'),
        ('ptokens', '0006_ptokenevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='ptokenevent',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='token_events', to='dashboard.Profile'),
        ),
        migrations.AlterField(
            model_name='ptokenevent',
            name='event',
            field=models.CharField(choices=[('mint_ptoken', 'Mint tokens'), ('burn_ptoken', 'Burn tokens'), ('update_supply', 'Update ptoken supply'), ('edit_price_ptoken', 'Update price token')], max_length=20),
        ),
    ]
