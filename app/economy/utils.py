from economy.models import ConversionRate

# All Units in native currency


class TransactionException(Exception):
    pass



def convert_amount(from_amount, from_currency, to_currency):
    latest_conversion_rate = ConversionRate.objects.filter(
        from_currency=from_currency,
        to_currency=to_currency
        ).order_by('-timestamp').first()
    return (latest_conversion_rate.to_amount / latest_conversion_rate.from_amount) * from_amount
