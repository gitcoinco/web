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


from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'sorts quests into difficulty categories based upon their success percentages '

    def handle(self, *args, **options):
        from quests.models import Quest

        for quest in Quest.objects.filter(visible=True):
            pct = quest.success_pct
            ac = quest.attempts.count()
            old_difficulty = quest.difficulty
            if ac > 3:
                if pct > 45:
                    quest.difficulty = "Beginner"
                elif pct > 20:
                    quest.difficulty = "Intermediate"
                elif pct > 10:
                    quest.difficulty = "Hard"
                else:
                    quest.difficulty = "Expert"
                quest.save()
                print(pct, "    ", ac, f"                      {old_difficulty} =>  {quest.difficulty}      ", quest.url)
