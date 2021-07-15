from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from dashboard.models import Profile


class Command(BaseCommand):

    help = 'create anonymous user profiles to ingest off-site grant donations'

    def handle(self, *args, **kwargs):

        with open('/code/scripts/input/givingblock_txns_nybw.csv', newline='', encoding="utf-8") as csvfile:
            num_rows = sum(1 for line in csvfile)
            for i in range(num_rows):
                random_string = get_random_string(length=32)
                # username is longer than github allows to prevent anon account hijack
                anonuser = User.objects.create_user(username='anonusergitcoin{}-{}'.format(i, random_string),
                                                    email='anonusergitcoin{}@example.com'.format(i),
                                                    password=random_string)
                anonprofile = Profile.objects.create(data={},
                                                     user=anonuser,
                                                     handle=anonuser.username,
                                                     email=anonuser.email)
