from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from app.utils import sync_profile
from dashboard.models import Organization, Profile, Repo
from git.utils import get_organization, get_repo, get_user


class Command(BaseCommand):
    help = 'Synchronizes Organizations and Repo roles to members'

    def handle(self, *args, **options):

        try:
            print("Loading Users....")
            all_users = User.objects.filter(
                is_active=True, profile__isnull=False)

            synced = []

            def recursive_sync(lsynced, handle):
                print("lysnced is")
                print(lsynced)
                try:

                    if handle not in lsynced:

                        print(f'Syncing User Handle: {handle}')
                        profile = sync_profile(handle)
                        access_token = profile.user.social_auth.filter(provider='github').latest('pk').access_token
                        print('Removing Stale Organizations and Groups')
                        remove_org_groups = [x for x in profile.orgs.all() if x.name not in profile.organizations]
                        for y in remove_org_groups:
                            profile.orgs.remove(y)
                            profile.user.groups.filter(name__contains=y.name).delete()
                        print('getting repos')
                        user_access_repos = get_repo(handle, '/repos', (handle, access_token), is_user=True)
                        # Question around user repo acccess if we can't get user repos, should we assume all repos are no longer available in the platform?

                        if 'message' not in user_access_repos:
                            print('got repos')
                            current_user_repos = []
                            for y in user_access_repos:
                                current_user_repos.append(y['name'])
                            remove_user_repos_names = [x for x in profile.repos.all() if
                                                       x.name not in current_user_repos]

                            remove_user_repos = Repo.objects.filter(name__in=remove_user_repos_names,
                                                                    profile__handle=handle)
                            for y in remove_user_repos:
                                profile.repos.remove(y)
                        print('appending to lsynced: {}'.format(handle))
                        lsynced.append(handle)
                    else:
                        return lsynced

                    members_to_sync = []

                    for org in profile.organizations:
                        db_org = Organization.objects.get_or_create(name=org)[0]
                        print(f'Syncing Organization: {db_org.name}')
                        profile.orgs.add(db_org)

                        org_members = get_organization(
                            db_org.name,
                            '/members'
                        )
                        for member in org_members:
                            member_user_obj = User.objects.get(
                                profile__handle=member['login'],
                                is_active=True
                            )

                            if member_user_obj is None:
                                continue

                            membership = get_organization(
                                db_org.name,
                                f'/memberships/{member["login"]}'
                            )

                            role = membership['role'] if not None else "member"
                            db_group = Group.objects.get_or_create(name=f'{db_org.name}-role-{role}')

                            db_org.groups.add(db_group[0])
                            member_user_obj.groups.add(db_group[0])
                            members_to_sync.append(member['login'])
                            # lsynced = recursive_sync(lsynced, member['login']) if not None else []

                        org_repos = get_organization(
                            db_org.name,
                            '/repos'
                        )

                        for repo in org_repos:
                            db_repo = Repo.objects.get_or_create(name=repo['name'])[0]
                            db_org.repos.add(db_repo)
                            print(f'Syncing Repo: {db_repo.name}')
                            repo_collabs = get_repo(
                                repo['full_name'],
                                '/collaborators',
                                (handle, access_token)
                            )
                            if 'message' not in repo_collabs:
                                for collaborator in repo_collabs:
                                    member_user_obj = User.objects.get(profile__handle=collaborator['login'],
                                                                       is_active=True)
                                    if member_user_obj is None:
                                        continue
                                    member_user_profile = Profile.objects.get(handle=collaborator['login'])

                                    if collaborator['permissions']['admin']:
                                        permission = "admin"
                                    elif collaborator['permissions']['push']:
                                        permission = "write"
                                    elif collaborator['permissions']['pull']:
                                        permission = "pull"
                                    else:
                                        permission = "none"

                                    db_group = Group.objects.get_or_create(
                                        name=f'{db_org.name}-repo-{repo["name"]}-{permission}')[0]
                                    db_org.groups.add(db_group)
                                    member_user_obj.groups.add(db_group)
                                    member_user_profile.repos.add(db_repo)
                                    if collaborator['login'] not in members_to_sync or collaborator[
                                        'login'] not in lsynced:
                                        members_to_sync.append(collaborator['login'])
                                    for x in members_to_sync:
                                        lsynced = lsynced + recursive_sync(lsynced, x)

                        return lsynced
                except Exception as exc:
                    print(exc)

            for user in all_users:
                # get profile data now creates or gets the new organization data for each user
                print('syncing user {}'.format(user.profile.handle))
                synced = recursive_sync(synced, user.profile.handle)
            print("Sync Completed")
        except ValueError as e:
            print(e)
