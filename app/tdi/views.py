'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import WhitepaperAccess, AccessCodes, WhitepaperAccessRequest
from django.template.response import TemplateResponse
from django.core.validators import validate_email
from django.conf import settings
from pyPdf import PdfFileWriter, PdfFileReader
from marketing.mails import send_mail
from ratelimit.decorators import ratelimit
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from wsgiref.util import FileWrapper
from retail.helpers import get_ip
import os
import StringIO


def ratelimited(request, ratelimited=False):
    return whitepaper_access(request, ratelimited=True)

@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def whitepaper_new(request, ratelimited=False):

    context = {
        'active': 'whitepaper',
        'title': 'Whitepaper',
        'minihero': 'Whitepaper',
        'suppress_logo': True,
        }
    if not request.POST.get('submit', False):
        return TemplateResponse(request, 'whitepaper_new.html', context)

    if ratelimited:
        context['msg'] = "You're ratelimited.  Please contact founders@gitcoin.co"
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    context['role'] = request.POST.getlist('role')
    context['email'] = request.POST.get('email')
    context['comments'] = request.POST.get('comments')
    ip = get_ip(request)
    body = """
Email: {} \n
Role: {}\n
Comments: {}\n
IP: {}\n

    """.format(context['email'], context['role'], context['comments'], ip)
    send_mail(settings.CONTACT_EMAIL, settings.CONTACT_EMAIL, "New Whitepaper Request", str(body))

    war = WhitepaperAccessRequest.objects.create(
        email=context['email'],
        role=context['role'],
        comments=context['comments'],
        ip=ip,
    )


    valid_email = True
    try:
        validate_email(request.POST.get('email', False))
    except Exception as e:
        valid_email = False

    if not request.POST.get('email', False) or not valid_email:
        context['msg'] = "Invalid Email.  Please contact founders@gitcoin.co"
        return TemplateResponse(request, 'whitepaper_new.html', context)

    context['msg'] = "Your request has been sent."
    return TemplateResponse(request, 'whitepaper_new.html', context)


#@ratelimit(key='ip', rate='1/m', block=True)
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def whitepaper_access(request, ratelimited=False):

    context = {
        'active': 'whitepaper',
        'title': 'Whitepaper',
        'minihero': 'Whitepaper',
        'suppress_logo': True,
        }
    if not request.POST.get('submit', False):
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    if ratelimited:
        context['msg'] = "You're ratelimited.  Please contact founders@gitcoin.co"
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)


    context['accesskey'] = request.POST.get('accesskey')
    context['email'] = request.POST.get('email')
    access_codes = AccessCodes.objects.filter(invitecode=request.POST.get('accesskey'))
    valid_access_code = access_codes.exists()
    if not valid_access_code:
        context['msg'] = "Invalid Access Code.  Please contact founders@gitcoin.co"
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    ac = access_codes.first()
    if ac.uses >= ac.maxuses:
        context['msg'] = "You have exceeded your maximum number of uses for this access code.  Please contact founders@gitcoin.co"
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    valid_email = True
    try:
        validate_email(request.POST.get('email', False))
    except Exception as e:
        valid_email = False

    if not request.POST.get('email', False) or not valid_email:
        context['msg'] = "Invalid Email.  Please contact founders@gitcoin.co"
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    ip = get_ip(request)
   
    wa = WhitepaperAccess.objects.create(
        invitecode=request.POST.get('accesskey', False),
        email=request.POST.get('email', False),
        ip=ip,
    )

    send_mail(settings.CONTACT_EMAIL, settings.CONTACT_EMAIL, "New Whitepaper Generated", str(wa))

    # bottom watermark
    packet1 = StringIO.StringIO()
    can = canvas.Canvas(packet1, pagesize=letter)

    grey = Color(22/255, 6/255, 62/255, alpha=0.3)
    can.setFillColor(grey)
    can.setFontSize(8)
    lim = 30
    email__etc = wa.email if len(wa.email) < lim else wa.email[0:lim] + "..."
    msg = "Generated for access code {} by email {} at {} via ip: {}. https://gitcoin.co/whitepaper".format(wa.invitecode, email__etc, wa.created_on.strftime("%Y-%m-%d %H:%M"), wa.ip)
    charlength = 3.5
    width = len(msg) * charlength
    left = (600 - width)/2
    can.drawString(left, 7, msg)
    can.save()


    # middle watermark
    packet2 = StringIO.StringIO()
    can = canvas.Canvas(packet2, pagesize=letter)
    grey = Color(22/255, 6/255, 62/255, alpha=0.02)
    can.setFillColor(grey)
    can.setFontSize(100)
    msg = "WP{}".format(str(wa.pk).zfill(5))
    charlength = 55
    width = len(msg) * charlength
    left = (600 - width)/2
    can.rotate(45)
    can.drawString(320, 50, msg)
    can.save()


    #move to the beginning of the StringIO buffer
    file_name = 'whitepaper.pdf'
    path_to_file = 'assets/other/wp.pdf'
    new_pdf1 = PdfFileReader(packet1)
    new_pdf2 = PdfFileReader(packet2)
    # read your existing PDF
    existing_pdf = PdfFileReader(file(path_to_file, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    try:
        for i in range(0, 50):
            page = existing_pdf.getPage(i)
            page.mergePage(new_pdf1.getPage(0))
            if i != 0:
                page.mergePage(new_pdf2.getPage(0))
            output.addPage(page)
    except Exception as e:
        print(e)
    # finally, write "output" to a real file
    outputfile = "output/whitepaper_{}.pdf".format(wa.pk)
    outputStream = file(outputfile, "wb")
    output.write(outputStream)
    outputStream.close()

    filename = outputfile                       
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/pdf')
    response['Content-Length'] = os.path.getsize(filename)
    return response

