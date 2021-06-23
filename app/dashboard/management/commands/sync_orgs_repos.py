from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from app.utils import sync_profile
from dashboard.models import Organization, Profile, Repo
from git.utils import get_organization, get_user, github_connect


class Command(BaseCommand):
    help = 'Synchronizes Organizations and Repo roles to members'

    def handle(self, *args, **options):

        def recursive_sync(lsynced, handle):
            try:

                if handle not in lsynced:

                    print(f'Syncing User Handle: {handle}')
                    profile = sync_profile(handle)
                    print('Profile from sync')
                    print(profile)
                    access_token = profile.user.social_auth.filter(provider='github').latest('pk').access_token
                    print('Removing Stale Organizations and Groups')
                    remove_org_groups = [
                        x for x in profile.profile_organizations.all() if x.name not in profile.organizations
                    ]
                    for y in remove_org_groups:
                        profile.profile_organizations.remove(y)
                        profile.user.groups.filter(name__contains=y.name).delete()
                        print(f'Removing: {profile.handle} from Organization: {y.name} ')

                    try:
                        gh_client = github_connect(access_token)
                        user_access_repos = gh_client.get_user().get_repos()
                        if user_access_repos.totalCount: pass # trigger error throw if any
                        # Question around user repo access if we can't get user repos, should we assume all repos are no longer available in the platform?
                    except Exception as e:
                        print(e.data['message'])
                        return lsynced

                    current_user_repos = []
                    for y in user_access_repos:
                        current_user_repos.append(y.name)

                    remove_user_repos_names = [x for x in profile.repos.all() if x.name not in current_user_repos]

                    remove_user_repos = Repo.objects.filter(name__in=remove_user_repos_names, profile__handle=handle)
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
                    try:
                        if org in orgs_synced:
                            print(f'{org} has been synced already')
                            continue

                        orgs_synced.append(org)
                        db_org = Organization.objects.get_or_create(name=org)[0]

                        print(f'Syncing Organization: {db_org.name}')
                        profile.profile_organizations.add(db_org)

                        try:
                            gh_client = github_connect()
                            org_members = gh_client.get_organization(db_org.name).get_members()
                            if org_members.totalCount: pass # trigger error throw if any
                        except Exception as e:
                            print(e.data['message'])
                            continue

                        for member in org_members:

                            try:
                                membership = get_organization(
                                    db_org.name, f'/memberships/{member["login"]}', (handle, access_token)
                                )
                                if 'message' in membership:
                                    print(membership['message'])
                                    continue
                                role = membership['role'] if 'role' in membership else "member"
                                db_group = Group.objects.get_or_create(name=f'{db_org.name}-role-{role}')[0]
                                db_org.groups.add(db_group)
                                member_profile_obj = Profile.objects.get(handle=member['login'], user__is_active=True)
                                member_profile_obj.user.groups.add(db_group)
                                members_to_sync.append(member['login'])
                            except Exception as e:
                                # print(f'An exception happened in the Organization Loop: handle {member["login"]} {e}')
                                continue

                        try:
                            gh_client = github_connect(access_token)
                            org_repos = gh_client.get_organization(db_org.name).get_repos()
                            if org_repos.totalCount: pass # trigger error throw if any
                        except Exception as e:
                            print(e.data['message'])
                            continue

                        for repo in org_repos:
                            db_repo = Repo.objects.get_or_create(name=repo.name)[0]
                            db_org.repos.add(db_repo)
                            print(f'Syncing Repo: {db_repo.name}')
                            try:
                                gh_client = github_connect(access_token)
                                repo_collabs = gh_client.get_repo(repo.full_name).get_collaborators()
                                if repo_collabs.totalCount: pass # trigger error throw if any
                            except Exception as e:
                                print(e.data['message'])
                                continue

                            for collaborator in repo_collabs:
                                
                                if collaborator.permissions:
                                    if collaborator.permissions.admin:
                                        permission = "admin"
                                    elif collaborator.permissions.push:
                                        permission = "write"
                                    elif collaborator.permissions.pull:
                                        permission = "pull"
                                    else:
                                        permission = "none"

                                    db_group = Group.objects.get_or_create(
                                        name=f'{db_org.name}-repo-{repo["name"]}-{permission}'
                                    )[0]
                                    db_org.groups.add(db_group)

                                    try:
                                        member_user_profile = Profile.objects.get(
                                            handle=collaborator.login, user__is_active=True
                                        )
                                        member_user_profile.user.groups.add(db_group)
                                        member_user_profile.repos.add(db_repo)
                                        if collaborator.login not in members_to_sync or \
                                            collaborator.login not in lsynced:
                                            members_to_sync.append(collaborator.login)
                                    except Exception as e:
                                        continue

                        for x in members_to_sync:
                            try:
                                lsynced = lsynced + recursive_sync(lsynced, x)
                            except Exception as e:
                                # print(f'An exception happened in the Members sync Loop: handle: {handle} {e}')
                                continue
                    except Exception as e:
                        # print(f'An exception happened in the Organization Loop: handle {handle} {e}')
                        continue
            except Exception as exc:
                print(f'Exception occurred inside recursive_sync: {exc}')

            return lsynced

        try:

            print("Loading Users....")
            all_users = Profile.objects.filter(user__is_active=True).prefetch_related('user')

            synced = []
            orgs_synced = []
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
