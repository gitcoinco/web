'''
    Copyright (C) 2019 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
import os
from io import BytesIO
from secrets import token_hex
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import translation
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from marketing.mails import send_mail, setup_lang
from marketing.utils import invite_to_slack
from PyPDF2 import PdfFileReader, PdfFileWriter
from ratelimit.decorators import ratelimit
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from retail.helpers import get_ip

from .models import AccessCodes, WhitepaperAccess, WhitepaperAccessRequest


def ratelimited(request, ratelimited=False):
    return whitepaper_access(request, ratelimited=True)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def whitepaper_new(request, ratelimited=False):

    context = {
        'active': 'whitepaper',
        'title': _('Whitepaper'),
        'minihero': _('Whitepaper'),
        'suppress_logo': True,
    }
    if not request.POST.get('submit', False):
        return TemplateResponse(request, 'whitepaper_new.html', context)

    if ratelimited:
        context['msg'] = _("You're ratelimited. Please contact founders@gitcoin.co")
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    context['role'] = request.POST.getlist('role')
    context['email'] = request.POST.get('email')
    context['comments'] = request.POST.get('comments')
    context['success'] = True
    ip = get_ip(request)
    body = gettext("""
Email: {} \n
Role: {}\n
Comments: {}\n
IP: {}\n

https://gitcoin.co/_administration/tdi/whitepaperaccessrequest/

    """).format(context['email'], context['role'], context['comments'], ip)
    send_mail(
        settings.CONTACT_EMAIL,
        settings.CONTACT_EMAIL,
        _("New Whitepaper Request"),
        str(body),
        categories=['admin', 'whitepaper_request'],
    )

    WhitepaperAccessRequest.objects.create(
        email=context['email'],
        role=context['role'],
        comments=context['comments'],
        ip=ip,
    )

    for code in AccessCodes.objects.all():
        print(code)

    invite_to_slack(context['email'])

    valid_email = True
    try:
        validate_email(request.POST.get('email', False))
    except ValidationError:
        valid_email = False

    if not request.POST.get('email', False) or not valid_email:
        context['msg'] = _("Invalid Email. Please contact founders@gitcoin.co")
        context['success'] = False
        return TemplateResponse(request, 'whitepaper_new.html', context)

    context['msg'] = _("Your request has been sent.  <a href=/slack>Meantime, why don't you check out the slack channel?</a>")
    return TemplateResponse(request, 'whitepaper_new.html', context)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def whitepaper_access(request, ratelimited=False):

    context = {
        'active': 'whitepaper',
        'title': _('Whitepaper'),
        'minihero': _('Whitepaper'),
        'suppress_logo': True,
        }
    if not request.POST.get('submit', False):
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    if ratelimited:
        context['msg'] = _("You're ratelimited. Please contact founders@gitcoin.co")
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    context['accesskey'] = request.POST.get('accesskey')
    context['email'] = request.POST.get('email')
    access_codes = AccessCodes.objects.filter(invitecode=request.POST.get('accesskey'))
    valid_access_code = access_codes.exists()
    if not valid_access_code:
        context['msg'] = _("Invalid Access Code. Please contact founders@gitcoin.co")
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    ac = access_codes.first()
    if ac.uses >= ac.maxuses:
        context['msg'] = _("You have exceeded your maximum number of uses for this access code. Please contact founders@gitcoin.co")
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    valid_email = True
    try:
        validate_email(request.POST.get('email', False))
    except Exception as e:
        valid_email = False

    if not request.POST.get('email', False) or not valid_email:
        context['msg'] = _("Invalid Email. Please contact founders@gitcoin.co")
        return TemplateResponse(request, 'whitepaper_accesscode.html', context)

    ip = get_ip(request)

    wa = WhitepaperAccess.objects.create(
        invitecode=request.POST.get('accesskey', False),
        email=request.POST.get('email', False),
        ip=ip,
    )

    send_mail(
        settings.CONTACT_EMAIL,
        settings.CONTACT_EMAIL,
        _("New Whitepaper Generated"),
        str(wa),
        categories=['admin', 'whitepaper_gen'],
    )

    # bottom watermark
    packet1 = BytesIO()
    can = canvas.Canvas(packet1, pagesize=letter)

    grey = Color(22/255, 6/255, 62/255, alpha=0.3)
    can.setFillColor(grey)
    can.setFontSize(8)
    lim = 30
    email__etc = wa.email if len(wa.email) < lim else wa.email[0:lim] + "..."
    msg = gettext("Generated for access code {} by email {} at {} via ip: {}. https://gitcoin.co/whitepaper").format(wa.invitecode, email__etc, wa.created_on.strftime("%Y-%m-%d %H:%M"), wa.ip)
    charlength = 3.5
    width = len(msg) * charlength
    left = (600 - width)/2
    can.drawString(left, 7, msg)
    can.save()

    # middle watermark
    packet2 = BytesIO()
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

    # move to the beginning of the StringIO buffer
    path_to_file = 'assets/other/wp.pdf'
    new_pdf1 = PdfFileReader(packet1)
    new_pdf2 = PdfFileReader(packet2)
    # read your existing PDF

    existing_pdf = PdfFileReader(open(path_to_file, "rb"))
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
    outputStream = open(outputfile, "wb")
    output.write(outputStream)
    outputStream.close()

    filename = outputfile
    wrapper = FileWrapper(open(filename, 'rb'))

    response = HttpResponse(wrapper, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="GitcoinWhitepaper.pdf"'
    response['Content-Length'] = os.path.getsize(filename)
    return response


@staff_member_required
def process_accesscode_request(request, pk):

    obj = WhitepaperAccessRequest.objects.get(pk=pk)
    context = {
        'obj': obj,
    }

    if obj.processed:
        raise

    if request.POST.get('submit', False):
        invitecode = token_hex(16)[:29]

        AccessCodes.objects.create(
            invitecode=invitecode,
            maxuses=1,
        )
        obj.processed = True
        obj.save()

        from_email = settings.PERSONAL_CONTACT_EMAIL
        to_email = obj.email
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            subject = request.POST.get('subject')
            body = request.POST.get('body').replace('[code]', invitecode)
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("Kevin from Gitcoin.co"),
                categories=['admin', 'access_code_request'],
            )
            messages.success(request, _('Invite sent'))
        finally:
            translation.activate(cur_language)

        return redirect('/_administration/tdi/whitepaperaccessrequest/?processed=False')

    return TemplateResponse(request, 'process_accesscode_request.html', context)
