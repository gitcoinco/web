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
import logging
from tempfile import NamedTemporaryFile

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.utils import create_user_action
from git.utils import org_name
from PIL import Image, ImageOps

from .models import Avatar
from .utils import add_gitcoin_logo_blend, build_avatar_svg, get_avatar, get_err_response, handle_avatar_payload

logger = logging.getLogger(__name__)


def avatar(request):
    """Serve an avatar."""
    skin_tone = f"#{request.GET.get('skin_tone', '3F2918')}"
    preview = request.GET.get('preview', False)
    payload = {
        'background_color': f"#{request.GET.get('background', '781623')}",
        'icon_size': (int(request.GET.get('icon_width', 215)), int(request.GET.get('icon_height', 215))),
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
def save_avatar(request):
    """Save the Avatar configuration."""
    response = {'status': 200, 'message': 'Avatar saved'}
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        return JsonResponse({'status': 405, 'message': 'Authentication required'}, status=405)

    profile = request.user.profile

    if request.body and 'use_github_avatar' in str(request.body):
        if not profile.avatar:
            profile.avatar = Avatar.objects.create()
            profile.save()
        profile.avatar.use_github_avatar = True
        avatar_url = profile.avatar.pull_github_avatar()
        response['message'] = 'Avatar updated'
        response['avatar_url'] = avatar_url
        return JsonResponse(response, status=200)

    payload = handle_avatar_payload(request)
    try:
        if not profile.avatar:
            profile.avatar = Avatar.objects.create(config=payload, use_github_avatar=False)
            profile.save()
        else:
            profile.avatar.config = payload
            profile.avatar.use_github_avatar = False
            profile.avatar.save()
        response['message'] = 'Avatar updated'
        profile.avatar.create_from_config(svg_name=profile.handle)
        create_user_action(profile.user, 'updated_avatar', request)
    except Exception as e:
        response['status'] = 400
        response['message'] = 'Bad Request'
        logger.error(e)
    return JsonResponse(response, status=response['status'])


def handle_avatar(request, org_name='', add_gitcoincologo=False):
    from dashboard.models import Profile
    icon_size = (215, 215)

    if org_name:
        try:
            profile = Profile.objects.select_related('avatar').get(handle__iexact=org_name)
            if profile.avatar:
                if profile.avatar.use_github_avatar and profile.avatar.png:
                    return HttpResponse(profile.avatar.png.file, content_type='image/png')
                if profile.avatar.svg and not profile.avatar.use_github_avatar:
                    return HttpResponse(profile.avatar.svg.file, content_type='image/svg+xml')
        except Exception as e:
            logger.error(e)

    # default response
    # params
    repo_url = request.GET.get('repo', False)
    if not org_name and (not repo_url or 'github.com' not in repo_url):
        return get_err_response(request, blank_img=(org_name == 'Self'))

    try:
        # get avatar of repo
        if not org_name:
            org_name = org_name(repo_url)

        filepath = get_avatar(org_name)

        # new image
        img = Image.new('RGBA', icon_size, (255, 255, 255))

        # execute
        avatar = Image.open(filepath, 'r').convert("RGBA")
        avatar = ImageOps.fit(avatar, icon_size, Image.ANTIALIAS)
        offset = 0, 0
        img.paste(avatar, offset, avatar)

        # Determine if we should add the Gitcoin logo
        if add_gitcoincologo and org_name != 'gitcoinco':
            img = add_gitcoin_logo_blend(avatar, icon_size)

        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')
        return response
    except (AttributeError, IOError, SyntaxError) as e:
        logger.error(e)
        return get_err_response(request, blank_img=(org_name == 'Self'))
