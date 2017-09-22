from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import premailer


@staff_member_required
def template(request):

    params = {}

    response_html = premailer.transform(render_to_string("emails/template.html", params, request=request))
    response_txt = render_to_string("emails/template.txt", params, request=request)

    return HttpResponse(response_html)
