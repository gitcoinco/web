import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from economy.utils import convert_amount
from gas.models import GasAdvisory, GasProfile


def recommend_min_gas_price_to_confirm_in_time(minutes, default=5):
    # if settings.DEBUG:
    #     return 10
    try:
        gp = GasProfile.objects.filter(
            created_on__gt=(timezone.now()-timezone.timedelta(minutes=31)),
            mean_time_to_confirm_minutes__lt=minutes
            ).order_by('gas_price').first()
        return max(gp.gas_price, 1)
    except Exception:
        return default


def gas_price_to_confirm_time_minutes(gas_price):
    gp = GasProfile.objects.get(
        created_on__gt=(timezone.now()-timezone.timedelta(minutes=31)),
        gas_price=gas_price)
    return gp.mean_time_to_confirm_minutes


def eth_usd_conv_rate():
    from_amount = 1
    from_currency = 'ETH'
    to_currency = 'USDT'
    return convert_amount(from_amount, from_currency, to_currency)


def conf_time_spread(max_gas_price=9999):
    try:
        for minutes in [1, 11, 21, 31]:
            gp = GasProfile.objects.filter(
                created_on__gt=(timezone.now()-timezone.timedelta(minutes=minutes)),
                gas_price__lte=max_gas_price,
                ).distinct('gas_price').order_by('gas_price').values_list('gas_price', 'mean_time_to_confirm_minutes')
            if gp:
                return json.dumps(list(gp), cls=DjangoJSONEncoder)
    except Exception:
        pass
    return json.dumps([])


def gas_advisories():
    gas_advisories = GasAdvisory.objects.filter(active=True, active_until__gt=timezone.now())
    return gas_advisories
