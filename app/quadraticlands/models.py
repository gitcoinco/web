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

"""
# receive, use, knowledge 
class QuadLandsMission(models.Model):
    '''Establish database structure for QuadLands Missions'''
    '''
    Mission
        - created_on
        - title (varchar255)
        - reward (varchar255) # multiple rewards? kudos? tokens, recurring
        - prereq_mission(nullable fk)
        - url
        - re-playable (boolean) 
        - state (varchar255) # [production, dev, etc]
    ''' 
    created_on = models.DateTimeField()
    mission_title = models.CharField(max_length=100)
    # mission_reward = models.JSONField(null=True)
    replayable = models.BooleanField(default=True)
    state = models.CharField(default="dev", max_length=4) # dev, stag, prod 

class QuadLandsQuestion(models.Model):
    '''questions for the missions yo'''
    mission = models.ForeignKey(QuadLandsMission, on_delete=models.CASCADE)
    created_on = models.DateTimeField()
    answers = JSONField(default=dict)
"""
