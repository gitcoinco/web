# Generated by Django 2.2.4 on 2019-12-04 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0022_auto_20191115_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='background',
            field=models.CharField(blank=True, choices=[('red', 'red'), ('green', 'green'), ('blue', 'blue'), ('back0', 'back0'), ('back1', 'back1'), ('back2', 'back2'), ('back3', 'back3'), ('back4', 'back4'), ('back5', 'back5'), ('back6', 'back6'), ('back7', 'back7'), ('back8', 'back8'), ('back9', 'back9'), ('back10', 'back10'), ('back11', 'back11'), ('back12', 'back12'), ('back13', 'back13'), ('back14', 'back14'), ('back15', 'back15'), ('back16', 'back16'), ('back17', 'back17'), ('back18', 'back18'), ('back19', 'back19'), ('back20', 'back20'), ('back21', 'back21'), ('back22', 'back22'), ('back23', 'back23'), ('back24', 'back24'), ('back25', 'back25'), ('back26', 'back26'), ('back27', 'back27'), ('back28', 'back28'), ('back29', 'back29'), ('back30', 'back30'), ('back31', 'back31'), ('back32', 'back32'), ('back33', 'back33')], default='', max_length=100),
        ),
    ]
