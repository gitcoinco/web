def get_ip(request):
    forward_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward_for:
        ip_addr = forward_for.split(',')[0]
    else:
        ip_addr = request.META.get('REMOTE_ADDR')
    return ip_addr