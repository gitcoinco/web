# -*- coding: utf-8 -*-
"""Define the Avatar views.

Copyright (C) 2018 Gitcoin Core

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

"""
import json
import logging
from tempfile import NamedTemporaryFile

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.utils import create_user_action, is_blocked
from git.utils import org_name
from marketing.utils import is_deleted_account
from PIL import Image, ImageOps

from .models import BaseAvatar, CustomAvatar, SocialAvatar
from .utils import (
    add_gitcoin_logo_blend, build_avatar_svg, get_avatar, get_err_response, get_user_github_avatar_image,
    handle_avatar_payload,
)

logger = logging.getLogger(__name__)


def avatar(request):
    """Serve an avatar."""
    skin_tone = f"#{request.GET.get('skin_tone', '3F2918')}"
    preview = request.GET.get('preview', False)
    payload = {
        'background_color': f"#{request.GET.get('background', '781623')}",
        'icon_size': (
            int(request.GET.get('icon_width',
                                BaseAvatar.ICON_SIZE[0])), int(request.GET.get('icon_height', BaseAvatar.ICON_SIZE[1]))
        ),
        'avatar_size': request.GET.get('avatar_size', None),
        'skin_tone': skin_tone,
    }

    customizable_components = ['clothing', 'ears', 'head', 'hair']
    flat_components = ['eyes', 'mouth', 'nose']

    req = request.GET.copy()
    for component in customizable_components:
        if component in req:
            comp_color_key = f'{component}_color' if component not in ['ears', 'head'] else 'skin_tone'
            payload[component] = {
                'primary_color': f"#{req.get(comp_color_key, '18C708')}",
                'item_type': req.get(component)
            }

    for component in flat_components:
        if component in req:
            payload[component] = req.get(component)

    if preview:
        with NamedTemporaryFile(mode='w+', suffix='.svg') as tmp:
            avatar_preview = build_avatar_svg(payload=payload, temp=True)
            avatar_preview.save(tmp.name)
            with open(tmp.name) as file:
                response = HttpResponse(file, content_type='image/svg+xml')
                return response
    else:
        result_path = build_avatar_svg(payload=payload)

        with open(result_path) as file:
            response = HttpResponse(file, content_type='image/svg+xml')
        return response


@csrf_exempt
def save_github_avatar(request):
    """Save the Github Avatar."""
    response = {'status': 200, 'message': 'Avatar saved'}
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        return JsonResponse({'status': 405, 'message': 'Authentication required'}, status=405)
    profile = request.user.profile
    github_avatar_img = get_user_github_avatar_image(profile.handle)
    if not github_avatar_img:
        return JsonResponse(response, status=response['status'])

    with transaction.atomic():
        github_avatar = SocialAvatar.github_avatar(profile, github_avatar_img)
        github_avatar.save()
        profile.activate_avatar(github_avatar.pk)
        profile.save()
        create_user_action(profile.user, 'updated_avatar', request)
        response['message'] = 'Avatar updated'
        response['avatar_url'] = github_avatar.avatar_url
    return JsonResponse(response, status=response['status'])


@csrf_exempt
def save_custom_avatar(request):
    """Save the Custom Avatar."""
    response = {'status': 200, 'message': 'Avatar saved'}
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        return JsonResponse({'status': 405, 'message': 'Authentication required'}, status=405)
    profile = request.user.profile
    payload = handle_avatar_payload(json.loads(request.body))
    try:
        with transaction.atomic():
            custom_avatar = CustomAvatar.create(profile, payload)
            custom_avatar.save()
            profile.activate_avatar(custom_avatar.pk)
            profile.save()
            create_user_action(profile.user, 'updated_avatar', request)
            response['message'] = 'Avatar updated'
    except Exception as e:
        response['status'] = 500
        response['message'] = 'Internal error'
        logger.error('Save Avatar - Error: (%s) - Handle: (%s)', e, profile.handle if profile else '')
    return JsonResponse(response, status=response['status'])


def activate_avatar(request):
    """Activate the Avatar."""
    response = {'status': 200, 'message': 'Avatar activated'}
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        return JsonResponse({'status': 405, 'message': 'Authentication required'}, status=405)
    body = json.loads(request.body)
    avatar_to_activate_pk = body['avatarPk']
    profile = request.user.profile
    profile.activate_avatar(avatar_to_activate_pk)
    profile.save()
    create_user_action(profile.user, 'updated_avatar', request)
    return JsonResponse(response, status=response['status'])


def select_preset_avatar(request):
    """Select preset Avatar."""
    response = {'status': 200, 'message': 'Preset avatar selected'}
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        return JsonResponse({'status': 405, 'message': 'Authentication required'}, status=405)
    try:
        with transaction.atomic():
            body = json.loads(request.body)
            profile = request.user.profile
            preset_activate_pk = body['avatarPk']
            preset_avatar = CustomAvatar.objects.get(pk=preset_activate_pk)
            selected_avatar = preset_avatar.select(profile)
            selected_avatar.save()
            profile.activate_avatar(selected_avatar.pk)
            profile.save()
            create_user_action(profile.user, 'updated_avatar', request)
    except Exception as e:
        response['status'] = 400
        response['message'] = 'Bad Request'
        logger.error('Save Avatar - Error: (%s) - Handle: (%s)', e, profile.handle if profile else '')
    return JsonResponse(response, status=response['status'])


def handle_avatar(request, _org_name='', add_gitcoincologo=False):
    from dashboard.models import Profile
    icon_size = (215, 215)

    if _org_name:
        _org_name = _org_name.replace('@', '')

    if is_blocked(_org_name) or is_deleted_account(_org_name):
        return get_err_response(request, blank_img=(_org_name == 'Self'))

    if _org_name:
        try:
            profile = Profile.objects.prefetch_related('avatar_baseavatar_related')\
                .filter(handle__iexact=_org_name).first()
            if profile and profile.active_avatar:
                avatar_file, content_type = profile.active_avatar.determine_response(request.GET.get('email', False))
                if avatar_file:
                    return HttpResponse(avatar_file, content_type=content_type)
        except Exception as e:
            logger.error('Handle Avatar - Exception: (%s) - Handle: (%s)', str(e), _org_name)

    # default response
    # params
    repo_url = request.GET.get('repo', False)
    if not _org_name and (not repo_url or 'github.com' not in repo_url):
        return get_err_response(request, blank_img=(_org_name == 'Self'))

    try:
        # get avatar of repo
        if not _org_name:
            _org_name = org_name(repo_url)

        filepath = get_avatar(_org_name)

        # new image
        img = Image.new('RGBA', icon_size, (255, 255, 255))

        # execute
        avatar = Image.open(filepath, 'r').convert("RGBA")
        avatar = ImageOps.fit(avatar, icon_size, Image.ANTIALIAS)
        offset = 0, 0
        img.paste(avatar, offset, avatar)

        # Determine if we should add the Gitcoin logo
        if add_gitcoincologo and _org_name != 'gitcoinco':
            img = add_gitcoin_logo_blend(avatar, icon_size)

        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')
        return response
    except (AttributeError, IOError, SyntaxError) as e:
        logger.error('Handle Avatar - Response error: (%s) - Handle: (%s)', str(e), _org_name)
        return get_err_response(request, blank_img=(_org_name == 'Self'))
