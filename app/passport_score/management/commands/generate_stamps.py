import random
import traceback
from datetime import date, datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import numpy as np
import pandas as pd
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.models import GR15TrustScore


class Command(BaseCommand):
    help = "Generate random passports & stamps for testing"

    def handle(self, *args, **options):
        try:
            print(f"{datetime.now()} generating users ...")
            user_list = list(User.objects.values_list("id", "username"))
            
            # for i in range(5504, 50000):
            #     try:
            #         print(f"creating {i} / 50000")
            #         user = User.objects.create_user(username=f'test_user_{i}',
            #                             email=f'test_user_{i}@beatles.com',
            #                             password='glass onion')
            #         # user = User(username=f'test_user_{i}',
            #         #                     email=f'test_user_{i}@beatles.com',
            #         #                     password=make_password('glass onion'))
            #         # user_list.append(user)
            #     except Exception as exc:
            #         self.stdout.write(self.style.ERROR('ERROR: "%s"' % exc))

            # User.objects.bulk_create(user_list)
            # return
            # print(f"{datetime.now()}  saving users ...")
            # User.objects.bulk_create(user_list, 50000)
            # print(f"{datetime.now()}  DONE saving users ...")

            print(f"{datetime.now()}  delete passports ...")
            num_passports = Passport.objects.count()
            while num_passports > 0:
                print(f"{datetime.now()}  current count: {num_passports}")
                first_id = Passport.objects.order_by("id")[0].id
                Passport.objects.filter(id__lt=first_id+1000).delete()
                num_passports = Passport.objects.count()

            passports = []
            print("Num passports: ", len(passports))
            print(f"{datetime.now()}  create passports ...")
            for idx, (user_id, username) in enumerate(user_list):
                print(f"creating {idx} / {len(user_list)}")
                try:
                    passport = Passport(
                        user_id=user_id, did=username, passport={"type": username}
                    )
                    passports.append(passport)
                except Exception as exc:
                    self.stdout.write(self.style.ERROR('ERROR: "%s"' % exc))

            print(f"{datetime.now()}  save passports ...")
            Passport.objects.bulk_create(passports)
            print(f"{datetime.now()}  DONE save passports ...")

            passports = list(Passport.objects.all().values_list("id", "user_id"))
            print("Num new passports: ", len(passports))
            stamp_list = []
            for idx, passport in enumerate(passports):
                print(f"creating stamp for passport {idx} / {len(passports)}")
                try:
                    stamp_providers = list(
                        set(
                            [random.choice(providers) for i in range(random.randint(1, 61))]
                        )
                    )
                    stamps = [
                        PassportStamp(
                            passport_id=passport[0],
                            user_id=passport[1],
                            stamp_id=f"stamp_{idx}_{i}_{p}",
                            stamp_provider=p,
                        )
                        for i, p in enumerate(stamp_providers)
                    ]
                    stamp_list.extend(stamps)
                except Exception as exc:
                    self.stdout.write(self.style.ERROR('ERROR: "%s"' % exc))

            batch_size = 10000
            print(f"num stamps... {len(stamp_list)}")
            for i in range(0, len(stamp_list), batch_size):
                print(f"saving stamps... {i} / {len(stamp_list)}")
                PassportStamp.objects.bulk_create(stamp_list[i:i+batch_size])

        except Exception as exc:
            self.stdout.write(self.style.ERROR('ERROR: "%s"' % exc))
            # printing stack trace
            traceback.print_exc()
            raise CommandError("An unexpected error occured")
