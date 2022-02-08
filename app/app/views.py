from django.shortcuts import redirect

def redirect_view(request):
    response = redirect('http://decentralized.quadraticlands.com/')
    return response