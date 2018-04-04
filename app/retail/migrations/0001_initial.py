'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
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
                ('looking_for', models.CharField(choices=[('capital', 'capital'), ('builders', 'builders'), ('designers', 'designers'), ('customers', 'customers')], max_length=30)),
                ('have_already', models.CharField(choices=[('capital', 'capital'), ('builders', 'builders'), ('designers', 'designers'), ('customers', 'customers')], max_length=30))
            ],
            options={
                'abstract': False,
            },
        ),
    ]