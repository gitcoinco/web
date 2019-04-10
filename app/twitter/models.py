# -*- coding: utf-8 -*-
"""Define view for the inbox app.

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

from django.db import models

from economy.models import SuperModel


class TwitterLogin(SuperModel):
    """    Define database module used in Twitter login.    """
    id = models.AutoField(primary_key=True)
    request_token = models.CharField(max_length=36)
    access_token = models.CharField(max_length=56)
    access_secret = models.CharField(max_length=56)
    login_status = models.IntegerField()
    user_name = models.CharField(max_length=56)
    user_id = models.CharField(max_length=12)

    def __str__(self):
        return self.request_token
