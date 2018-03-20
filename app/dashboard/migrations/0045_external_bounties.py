# Generated by Django 2.0 on 2018-03-05 01:30

from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0044_auto_20180219_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalBounty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('url', models.URLField(db_index=True)),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('source_project', models.CharField(max_length=255)),
                ('amount', models.IntegerField(default=1)),
                ('amount_denomination', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_sync_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='tip',
            name='comments_priv',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='tip',
            name='comments_public',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='tip',
            name='from_address',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='tip',
            name='from_email',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='tip',
            name='from_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='tip',
            name='from_username',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='tip',
            name='github_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tip',
            name='receive_address',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='tip',
            name='receive_txid',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='tip',
            name='received_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
