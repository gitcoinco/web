from django.db import models

class CurrencyConversion(models.Model):
    """Model that represents an conversion transaciton between ETH and ERC-20 Tokens

    """

    from_amount = models.FloatField()
    to_amount = models.FloatField()
    conversion_rate = models.FloatField()
    txid = models.CharField(max_length=100, db_index=True)
    transaction_date = models.DateTimeField(null=False, db_index=True)
    from_token_addr = models.CharField(max_length=100, db_index=True)
    to_token_symbol = models.CharField(max_length=10, db_index=True)
    from_token_symbol =  models.CharField(max_length=10, db_index=True)
    transaction_result = models.CharField(max_length=10, default='success')
