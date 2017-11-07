from django.http import JsonResponse
from ratelimit.decorators import ratelimit


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def save(request):

    status = 422
    message = 'Please use a POST'

    if request.POST:
        bounty_id = request.POST.get('bounty_id')
        email_address = request.POST.get('email_address')
        direction = request.POST.get('direction')

        # TODO: Save
        # TODO: Send matching email
        status = 200
        message = 'Success'

    response = {
        'status': status,
        'message': message,
    }
    return JsonResponse(response)

