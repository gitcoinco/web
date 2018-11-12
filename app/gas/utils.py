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
        return max(0.1, gp.gas_price)
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
                created_on__gt=(timezone.now() - timezone.timedelta(minutes=minutes)),
                gas_price__lte=max_gas_price,
            ).distinct('gas_price').order_by('gas_price').values_list('gas_price', 'mean_time_to_confirm_minutes')
            if gp:
                return json.dumps(list(gp), cls=DjangoJSONEncoder)
    except Exception:
        pass
    return json.dumps([])


def gas_history(breakdown, mean_time_to_confirm_minutes):
    days = 30 * 8  # 8 months
    if breakdown == 'hourly':
        days = 10
    if breakdown == 'daily':
        days = 30 * 2
    if breakdown == 'weekly':
        days = 30 * 8
    start_date = (timezone.now()-timezone.timedelta(days=days))
    gas_profiles = GasProfile.objects.filter(
        created_on__gt=start_date,
        mean_time_to_confirm_minutes__lte=mean_time_to_confirm_minutes,
    ).order_by('-created_on')

    # collapse into best gas price per time period
    results = {}
    for gp in gas_profiles:
        if not gp.created_on.minute < 10:
            continue
        if not gp.created_on.hour < 1 and breakdown in ['daily', 'weekly']:
            continue
        if not gp.created_on.weekday() < 1 and breakdown in ['weekly']:
            continue
        key = gp.created_on.strftime("%Y-%m-%dT%H:00:00")
        package = {
            'created_on': key,
            'gas_price': float(gp.gas_price),
            'mean_time_to_confirm_minutes': float(gp.mean_time_to_confirm_minutes)
        }
        if key not in results.keys():
            results[key] = package
        else:
            key_package = results[key]
            if package['mean_time_to_confirm_minutes'] > key_package['mean_time_to_confirm_minutes']:
                results[key] = package
            elif package['mean_time_to_confirm_minutes'] == key_package['mean_time_to_confirm_minutes']:
                if package['gas_price'] < key_package['gas_price']:
                    results[key] = package
    # for debugging
    # for key, result in results.items():
    #    print(result['created_on'], result['gas_price'], result['mean_time_to_confirm_minutes'])

    # collapse into array that the frontend can understand
    results_array = []
    i = 0
    for key, val in results.items():
        results_array.append([val['gas_price'], i, val["created_on"]])
        i += 1
    return results_array


def gas_advisories():
    gas_advisories = GasAdvisory.objects.filter(active=True, active_until__gt=timezone.now())
    return gas_advisories
