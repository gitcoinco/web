from django.utils import timezone

from gas.models import GasProfile


def recommend_min_gas_price_to_confirm_in_time(minutes, default=5):
    try:
        gp = GasProfile.objects.filter(
            created_on__gt=(timezone.now()-timezone.timedelta(minutes=31)),
            mean_time_to_confirm_minutes__lt=minutes
            ).order_by('gas_price').first()
        return max(gp.gas_price, 1)
    except Exception as e:
        return default


def gas_price_to_confirm_time_minutes(gas_price):
    gp = GasProfile.objects.get(
        created_on__gt=(timezone.now()-timezone.timedelta(minutes=31)),
        gas_price=gas_price)
    return gp.mean_time_to_confirm_minutes
