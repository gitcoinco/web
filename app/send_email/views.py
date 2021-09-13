
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from rest_framework import permissions
from django.contrib.auth.models import User
from django.conf import settings

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def send_email(request):
    """
    Send the email to another user anonymously.
    """
    if settings.DEBUG:
        print(request.data)

    if request.method == 'POST':

        to_email_user_name = request.data["to_user_name"]
        from_email_user_name = request.data["from_user_name"]

        try:
            to_email_user = User.objects.get(username=to_email_user_name)
            from_email_user = User.objects.get(username=from_email_user_name)
        except Exception as e:
             return Response("User Not Found Error", status=status.HTTP_400_BAD_REQUEST)
         
        to_email_user_email = to_email_user.email
        from_email_user_email = from_email_user.email

        email_text = request.data["email_text"]
        email_subject = request.data["email_subject"]

        message = Mail(
            from_email=from_email_user_email,
            to_emails=to_email_user_email,
            subject=email_subject,
            html_content=email_text)

    if settings.DEBUG:
        print(message)

        try:
            # TODO: Use the proper API key here
            sg = SendGridAPIClient("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")
            response = sg.send(message)

            return Response("Success", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)



