from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from dashboard.models import Profile, Organization
from git.utils import get_organization, get_user, get_repo
from app.utils import sync_profile


class Command(BaseCommand):
    help = 'Synchronizes Organizations and Repo roles to members'

    def handle(self, *args, **options):

        try:
            print("Loading Users....")
            all_users = User.objects.all()  # potentially want to add some filters here around what users are synced
            print(all_users)
            print("Looking up Organization of user")
            # memoize the process so we only ever sync once per user

            synced = []

            def recursive_sync(lsynced, handle):
                try:
                    if handle not in lsynced:
                        print(f'Syncing User Handle: {handle}')
                        profile = sync_profile(handle)
                        print('Removing Stale Organizations and Groups')
                        remove = [x for x in profile.orgs.all() if x.name not in profile.organizations]
                        for y in remove:
                            profile.orgs.remove(y)
                            profile.user.groups.filter(name__contains=y.name).delete()
                        lsynced.append(handle)
                    else:
                        return lsynced

                    access_token = profile.user.social_auth.filter(provider='github').latest('pk').access_token
                    for org in profile.organizations:
                        db_org = Organization.objects.get_or_create(name=org)[0]
                        print(f'Syncing Org: {db_org.name}')
                        profile.orgs.add(db_org)
                        org_members = get_organization(
                            db_org.name,
                            '/members',
                            (profile.handle, access_token)
                        )

                        for member in org_members:

                            member_user_obj = User.objects.get(profile__handle=member['login'])

                            if member_user_obj is None:
                                continue

                            membership = get_organization(
                                db_org.name,
                                f'/memberships/{handle}',
                                (profile.handle, access_token)
                            )
                            role = membership['role'] if not None else "member"
                            group = Group.objects.get_or_create(name=f'{db_org.name}-role-{role}')

                            db_org.groups.add(group[0])
                            member_user_obj.groups.add(group[0])
                            lsynced = recursive_sync(lsynced, member['login']) if not None else []

                        org_repos = get_organization(
                            db_org.name,
                            '/repos',
                            (profile.handle, access_token)
                        )
                        for repo in org_repos:
                            repo_collabs = get_repo(
                                repo['full_name'],
                                '/collaborators',
                                (profile.handle, access_token)
                            )

                            for collaborator in repo_collabs:
                                member_user_obj = User.objects.get(profile__handle=collaborator['login'])

                                if member_user_obj is None:
                                    continue

                                if collaborator['permission']['admin']:
                                    permission = "admin"
                                elif collaborator['permission']['push']:
                                    permission = "write"
                                elif collaborator['permission']['pull']:
                                    permission = "pull"
                                else:
                                    permission = "none"

                                group = Group.objects.get_or_create(
                                    name=f'{db_org.name}-repo-{repo["name"]}-{permission}')
                                db_org.groups.add(group[0])
                                member_user_obj.groups.add(group[0])
                                lsynced = recursive_sync(lsynced, collaborator['login']) if not None else []

                    return lsynced
                except Exception as exc:
                    print(exc)

            for user in all_users:
                # get profile data now creates or gets the new organization data for each user
                synced = recursive_sync(synced, user.profile.handle)
                print("Profile Sync Completed")

        except ValueError as e:
            print(e)
