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
            all_users = Profile.objects.filter(
                user__is_active=True
            ).prefetch_related('user')

            synced = []
            orgs_synced = []

            def recursive_sync(lsynced, handle):
                try:

                    if handle not in lsynced:

                        print(f'Syncing User Handle: {handle}')
                        profile = sync_profile(handle)
                        access_token = profile.user.social_auth.filter(provider='github').latest('pk').access_token
                        print('Removing Stale Organizations and Groups')
                        remove_org_groups = [x for x in profile.profile_organizations.all() if
                                             x.name not in profile.organizations]
                        for y in remove_org_groups:
                            profile.profile_organizations.remove(y)
                            profile.user.groups.filter(name__contains=y.name).delete()
                            print(f'Removing: {profile.handle} from Organization: {y.name} ')

                        user_access_repos = get_repo(handle, '/repos', (handle, access_token), is_user=True)
                        # Question around user repo acccess if we can't get user repos, should we assume all repos are no longer available in the platform?

                        if 'message' in user_access_repos:
                            print(user_access_repos['message'])
                            return lsynced

                        current_user_repos = []
                        for y in user_access_repos:
                            current_user_repos.append(y['name'])

                        remove_user_repos_names = [x for x in profile.repos.all() if
                                                   x.name not in current_user_repos]

                        remove_user_repos = Repo.objects.filter(name__in=remove_user_repos_names,
                                                                profile__handle=handle)
                        for y in remove_user_repos:
                            profile.repos.remove(y)

                        lsynced.append(handle)
                    else:
                        return lsynced

                    members_to_sync = []
                    if profile.organizations is None:
                        print("no organizations to sync")
                        return []
                    for org in profile.organizations:
                        if org in orgs_synced:
                            continue

                        orgs_synced.append(org)
                        db_org = Organization.objects.get_or_create(name=org)[0]

                        print(f'Syncing Organization: {db_org.name}')
                        profile.profile_organizations.add(db_org)
                        org_members = get_organization(
                            db_org.name,
                            '/members'
                        )

                        if 'message' in org_members:
                            print(org_members['message'])
                            continue

                        for member in org_members:

                            try:

                                member_profile_obj = Profile.objects.get(
                                    handle=member['login'],
                                    user__is_active=True
                                )
                                membership = get_organization(
                                    db_org.name,
                                    f'/memberships/{member["login"]}'
                                )
                                role = membership['role'] if not None else "member"
                                db_group = Group.objects.get_or_create(name=f'{db_org.name}-role-{role}')[0]
                                db_org.groups.add(db_group)
                                member_profile_obj.user.groups.add(db_group)
                                members_to_sync.append(member['login'])
                                lsynced = recursive_sync(lsynced, member['login'])
                            except Exception as e:
                                print(f'Profile for Github Handle does not exist: {member["login"]}')
                                continue

                        org_repos = get_organization(
                            db_org.name,
                            '/repos'
                        )

                        if 'message' in org_repos:
                            print(org_repos['message'])
                            continue

                        for repo in org_repos:
                            db_repo = Repo.objects.get_or_create(name=repo['name'])[0]
                            db_org.repos.add(db_repo)
                            print(db_org)
                            print(f'Syncing Repo: {db_repo.name}')
                            repo_collabs = get_repo(
                                repo['full_name'],
                                '/collaborators',
                                (handle, access_token)
                            )
                            if 'message' in repo_collabs:
                                print(repo_collabs['message'])
                                continue

                            for collaborator in repo_collabs:
                                try:
                                    member_user_profile = Profile.objects.get(handle=collaborator['login'],
                                                                              user__is_active=True)

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
                                    member_user_profile.user.groups.add(db_group)
                                    member_user_profile.repos.add(db_repo)

                                    if collaborator['login'] not in members_to_sync or collaborator[
                                        'login'] not in lsynced:
                                        members_to_sync.append(collaborator['login'])
                                    for x in members_to_sync:
                                        print(x)
                                        try:
                                            lsynced = lsynced + recursive_sync(lsynced, x)
                                        except ValueError as members_loop_exec:

                                            print(members_loop_exec)
                                except Exception as e:
                                    print(e)
                                    continue

                        return lsynced
                except Exception as exc:
                    print(f'Unhandled Exception occurred: {exc}')

            for profile in all_users:
                try:
                    if profile.handle is not None:
                        synced = recursive_sync(synced, profile.handle)
                except ValueError as loop_exc:
                    print(f'Error syncing user id:{profile.user.id}')
                    print(loop_exc)
                except Exception as e:
                    print(e)

            print("Sync Completed")
        except ValueError as e:
            print(e)
