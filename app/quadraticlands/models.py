from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class InitialTokenDistribution(models.Model):
    '''This will be a read only model for a table that holds 
       the initial gitcoin retroactive token distribution information
    ''' 
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
