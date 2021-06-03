'''
    Copyright (C) 2021 Gitcoin Core

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
from django.utils import timezone


class Command(BaseCommand):

    help = 'sorts quests into difficulty categories based upon their success percentages '

    def handle(self, *args, **options):
        from quests.models import Quest

        # hide quests that have a low feedback ratio
        exempt_quests = [5]
        kwargs = {}
        kwargs['ui_data__feedbacks__feedback__isnull'] = False
        kwargs['ui_data__feedbacks__feedback__ne'] = []
        kwargs['ui_data__feedbacks__stats__-1__gt'] = 2
        kwargs['ui_data__feedbacks__ratio__lt'] = 0.3
        hide_quests = Quest.objects.filter(**kwargs).exclude(pk__in=exempt_quests, visible=False).order_by('ui_data__feedbacks__ratio')
        for quest in hide_quests:
            if not quest.force_visible:
                print(f'hiding {quest.pk}')
                quest.admin_comments = f"hidden on {timezone.now()} bc of low quality"
                quest.visible = False
                quest.save()

        # for all visibble quests, reclassify them
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
