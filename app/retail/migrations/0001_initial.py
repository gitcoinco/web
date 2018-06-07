# Generated by Django 2.0.3 on 2018-04-17 21:20

from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dashboard', '0050_auto_20180404_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(db_index=True, default=economy.models.get_time)),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('github_username', models.CharField(max_length=255)),
                ('summary', models.CharField(max_length=100)),
                ('more_info', models.CharField(max_length=500)),
                ('looking_for_capital', models.BooleanField()),
                ('looking_for_builders', models.BooleanField()),
                ('looking_for_designers', models.BooleanField()),
                ('looking_for_customers', models.BooleanField()),
                ('capital_exists', models.BooleanField()),
                ('builders_exists', models.BooleanField()),
                ('designers_exists', models.BooleanField()),
                ('customer_exists', models.BooleanField()),
                ('posts', models.IntegerField(default=0)),
                ('likes', models.IntegerField(default=0)),
                ('trending_score', models.IntegerField(default=101)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='ideas', to='dashboard.Profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
