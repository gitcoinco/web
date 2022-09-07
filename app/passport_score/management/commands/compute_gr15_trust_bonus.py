import traceback
from datetime import datetime

from django.core.management.base import BaseCommand

from passport_score.utils import get_new_trust_bonus, save_gr15_trustbonus_records


class Command(BaseCommand):
    help = "Calculates the APU score for GR15 based on the currently submitted passports & stamps"

    def handle(self, *args, **options):
        try:
            start = datetime.now()
            self.stdout.write(self.style.SUCCESS(f"{datetime.now()} START"))

            df_gr15_trust_bonus = get_new_trust_bonus().round(18)

            # df_gr15_trust_bonus_changed = df_gr15_trust_bonus.loc[
            #     df_gr15_trust_bonus.original_trust_bonus != df_gr15_trust_bonus.trust_bonus
            # ]

            # save_gr15_trustbonus_records(df_gr15_trust_bonus_changed)
            save_gr15_trustbonus_records(df_gr15_trust_bonus)

            self.stdout.write(self.style.SUCCESS("=" * 80))
            self.stdout.write(self.style.SUCCESS("%s" % df_gr15_trust_bonus))
            self.stdout.write(self.style.SUCCESS("%s" % str(df_gr15_trust_bonus.columns)))
            self.stdout.write(self.style.SUCCESS(f"{datetime.now()} DONE"))
            end = datetime.now()
            self.stdout.write(self.style.SUCCESS(f"DURATION {end - start}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"{e}"))
            traceback.print_tb()
