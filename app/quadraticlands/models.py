# -*- coding: utf-8 -*-
"""Define the quadraticlands views.

Copyright (C) 2020 Gitcoin Core

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

from django.contrib.postgres.fields import JSONField
from django.db import models


class InitialTokenDistribution(models.Model):
    '''Table for storing the initial gitcoin retroactive token distribution details''' 
    # manually set, no fk needed I don't think
    user_id = models.PositiveIntegerField(null=True)
    # need to confirm WEI is best stored in BigInt with django/pg 
    num_tokens = models.BigIntegerField()
    # do we need blank=True? This model will not interact with a form client side
    created_on = models.DateTimeField(null=True, blank=True)
    distribution = JSONField(default=dict)
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user_id}, {self.num_tokens}, {self.distribution}'

class MissionStatus(models.Model):
    ''' Track which missions a given user has completed'''
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='mission_status', on_delete=models.CASCADE
    )
    proof_of_use = models.BooleanField(default=False)
    proof_of_receive = models.BooleanField(default=False)
    proof_of_knowledge = models.BooleanField(default=False)
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.profile.id}, {self.proof_of_use}, {self.proof_of_receive}, {self.proof_of_knowledge}'
