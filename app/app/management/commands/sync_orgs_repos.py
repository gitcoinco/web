from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from dashboard.models import Profile, Organization
from git.utils import get_organization, get_user, get_repo
from app.utils import sync_profile


class Command(BaseCommand):
    help = 'Synchronizes Organizations and Repo roles to members'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):

        try:
            print("Loading Users....")
            all_users = User.objects.all()
            print(all_users)
            print("Looking up Organization of user")
            # memoize the process so we only ever sync once per user

            synced = []

            def recursive_sync(lsynced, handle):
                try:
                    if handle not in lsynced:
                        print(f'Syncing User Handle: {handle}')
                        profile = sync_profile(handle)
                        lsynced.append(handle)
                    else:
                        return lsynced

                    access_token = profile.user.social_auth.filter(provider='github').latest('pk').access_token
                    for org in profile.organizations.all():
                        print(f'Syncing Org: {org.name}')
                        org_members = get_organization(
                            org.name,
                            '/members',
                            (profile.handle, access_token)
                        )

                        # need a query that cleans out data that isn't in the current set we're processing
                        # drop users from organizations and the underlying groups when they aren't apart of membership
                        # or are not apart of the collaborators

                        for member in org_members:

                            member_user_obj = User.objects.get(profile__handle=member['login'])

                            if member_user_obj is None:
                                continue

                            membership = get_organization(
                                org.name,
                                f'/memberships/{handle}',
                                (profile.handle, access_token)
                            )
                            role = membership['role'] if not None else "member"
                            group = Group.objects.get_or_create(name=f'{org.name}-role-{role}')
                            org.groups.add(group[0])
                            member_user_obj.groups.add(group[0])
                            lsynced = recursive_sync(lsynced, member['login']) if not None else []

                        org_repos = get_organization(
                            org.name,
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

                                group = Group.objects.get_or_create(name=f'{org.name}-repo-{repo["name"]}-{permission}')
                                org.groups.add(group[0])
                                member_user_obj.groups.add(group[0])
                                lsynced = recursive_sync(lsynced, collaborator['login']) if not None else []

                    return lsynced
                except Exception as exc:
                    print("were over here")
                    print(exc)

            for user in all_users:
                # get profile data now creates or gets the new organization data for each user
                synced = recursive_sync(synced, user.profile.handle)
                print("Synced profiles")
                print(synced)

        except ValueError as e:
            print("were here")
            print(e)
