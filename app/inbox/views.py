from django.shortcuts import render
from inbox.models import Notification
from django.http import Http404, JsonResponse

# Create your views here.

def inbox(request, notification):
    try:
        notification = Notification.get(notification=notification)
        return notification
    except Exception as e:
        print(e)
        raise Http404
    return JsonResponse("Hello, world. You're at the polls index.")
