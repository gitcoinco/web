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

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Favorite

class FavoriteView(APIView):

    queryset = Favorite.objects.all()

    def get(self, request):
        print(request.user.is_authenticated)
        return Response({'hey':'there'})

    def post(self, request, format=None):
        print(request.user.is_authenticated)
        return Response({'hey':'there'})
