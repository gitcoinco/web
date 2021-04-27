from collections import defaultdict

from django.core.management.base import BaseCommand

from dashboard.models import Profile


# O(3n)  ~  or O(n) -- but n is 3 * profiles_total
def cleanup_x_user_id(x):
    print('\n\n\n%s:' % x)

    verfied_field = 'is_' + x + '_verified'
    identity_field = 'identity_data_' + x
    user_id_field = x + '_user_id'

    profiles_with_connection = Profile.objects.filter(**{ verfied_field: True })
    profiles_by_user_id = defaultdict(list)
    profiles_total = len(profiles_with_connection)

    # O(n)  ~  where n = profiles_total
    print('\n- %s profile%s have verified their %s id\n' % (profiles_total, ('s' if profiles_total == 0 or profiles_total > 1 else ''), x))
    for profile in profiles_with_connection:
        json_data = getattr(profile, identity_field)
        setattr(profile, user_id_field, json_data['id'])
        profiles_by_user_id[json_data['id']].append({'profile': profile, 'name': json_data['name']})

    total = len(profiles_by_user_id)
    current = 0

    # O(n)  ~  where n = profiles_total (we've grouped the profiles_by_user_id so the number of inputs is still the same even though we're iterating them in a nested for loop)
    print('\n-- %s unique %s__id entr%s discovered' % (total, identity_field, ('ies' if total == 0 or total > 1 else 'y')))
    for _id, entries in profiles_by_user_id.items():
        current += 1
        count = len(entries)
        if count <= 1:
            print('\n--- %s of %s -- no duplicates found for %s' % (current, total, entries[0]['name']))
            continue

        # Drop x trust badge for everyone with dupplicate x id
        print('\n--- %s of %s -- %s duplicates found for %s' % (current, total, count, entries[0]['name']))
        for data in entries:
            print('---- Clearing %s' % data['profile'].handle)
            setattr(data['profile'], verfied_field, False)
            setattr(data['profile'], user_id_field,  None)
            setattr(data['profile'], identity_field, {})

    # O(n)  ~  where n = profiles_total
    for profile in profiles_with_connection:
        profile.save()

    print('\n\n-- Finished saving all %ss\n' % user_id_field)


class Command(BaseCommand):

    help = 'cleans up profiles with duplicated verication ids for google and facebook'

    def handle(self, *args, **options):
        cleanup_x_user_id('google')
        cleanup_x_user_id('facebook')
