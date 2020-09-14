from dashboard.models import Earning

output = {}

counter = 0
queryset = Earning.objects.filter(network='mainnet')
for item in queryset.iter():
    counter += 1
    print(counter)
    _from = ''
    _to = ''
    try:
        _from = item.from_profile.handle
    except:
        pass
    try:
        _to = item.to_profile.handle
    except:
        pass
    for key in [_from, _to]:
        if key not in output.keys():
            output[key] = 0
        if item.value_usd:
            output[key] += item.value_usd

for key, val in output.items():
    print(key,",", val )
