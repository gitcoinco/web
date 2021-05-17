'''
    Copyright (C) 2019 Gitcoin Core

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
from django.contrib.auth.models import User
show_debug = False
from django.core.management.base import BaseCommand
import random
decimals = 18

class Command(BaseCommand):

    help = 'pulls user info'

    def handle(self, *args, **options):

        print('handle,user_id,total,active_user,kernel,GMV')
        for user in User.objects.filter(is_staff=True):
            kernel = random.randint(0, 100) * 10 ** 18
            active_user = random.randint(0, 100) * 10 ** 18
            GMV = random.randint(0, 100) * 10 ** 18
            total = kernel + active_user + GMV
            if hasattr(user, 'profile'):
                print(f"{user.profile.handle},{user.profile.id},{total},{active_user},{kernel},{GMV}")
