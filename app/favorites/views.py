# -*- coding: utf-8 -*-
"""Handle favorites views.

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

"""
import json
from fnmatch import filter

from django.http import JsonResponse

from dashboard.models import Bounty, Profile, User
from dashboard.router import BountySerializer, ProfileSerializer
from grants.models import Grant
from grants.router import GrantSerializer
from kudos.models import Token
from kudos.router import TokenSerializer
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Favorite


@api_view(['POST', 'DELETE'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def splitMethod_favorite(request, favType, id, **kwargs):
    if request.method == "DELETE":
        return delete_favorite(request, favType, id)
    elif request.method == "POST":
        return create_favorite(request, favType, id)


def create_favorite(request, favType, id, **kwargs):
    types = dict((val.lower(), key) for (key, val) in Favorite.TYPE)
    user = request.user
    #obj_id = request.data['id']
    obj_id = id
    #favType = request.data['favType']
    if favType not in types:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    newFav = Favorite()
    newFav.obj_id = obj_id
    newFav.user = user
    newFav.type = types[favType]
    if newFav.save():
        favSaveReturn = status.HTTP_201_CREATED
    else:
        favSaveReturn = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(favSaveReturn)

def delete_favorite(request,  favType, id, **kwargs):
    types = dict((val.lower(), key) for (key, val) in Favorite.TYPE)
    user = request.user
    obj_id = id
    #obj_id = request.data['id']
    #favType = request.data['favType']
    if favType not in types:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if Favorite.objects.filter(user=user, type=types[favType], obj_id=obj_id).delete():
        favSaveReturn = status.HTTP_200_OK
    else:
        favSaveReturn = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(favSaveReturn)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_favorites(request,  favType, **kwargs):
    reqTypes = dict((val.lower(), key) for (key, val) in Favorite.TYPE)
    user = request.user
    #favType = request.data['favType']
    if favType not in reqTypes:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    favs = Favorite.objects.filter(user=user, type=reqTypes[favType])
    jsonRetData = []
    for fav in favs:
        if reqTypes[favType] == "BOUN":
            for obj in Bounty.objects.filter(standard_bounties_id=fav.obj_id):
                ser = BountySerializer(obj)
                jsonRetData.append(ser.data)
        elif reqTypes[favType] == "KUDO":
            for obj in Token.objects.filter(id=fav.obj_id):
                ser = TokenSerializer(obj)
                jsonRetData.append(ser.data)
        elif reqTypes[favType] == "GRAN":
            for obj in Grant.objects.filter(id=fav.obj_id):
                ser = GrantSerializer(obj)
                jsonRetData.append(ser.data)
        elif reqTypes[favType] == "USER":
            for obj in Profile.objects.filter(id=fav.obj_id):
                ser = ProfileSerializer(obj)
                jsonRetData.append(ser.data)

    return Response(json.loads(json.dumps(jsonRetData, indent=4, sort_keys=True, default=str)))
