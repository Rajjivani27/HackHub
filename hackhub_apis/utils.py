import re
from .tokens import email_verification_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from HackHub.settings import EMAIL_HOST_USER
from django.http.request import HttpRequest
def media_processing(files) -> list:
    files_data = []

    for key,file_list in files:
            if key.startswith('media[') and key.endswith('].files'):
                files_data.append({'files':file_list[0]})

    return files_data

def send_verification_email(user,request):
    uid = urlsafe_base64_decode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_link = request.build_absolute_uri(
        reverse('verify_email_confirm',kwargs={'uid64':uid,'token':token})
    )

    subject = "Verify Email"
    message = f"Hii {user.username},\nPlease Verify your email by clicking below link:\n{verification_link}"
    to_user = user.email

    send_mail(
        subject,
        message,
        from_email= EMAIL_HOST_USER,
        recipient_list=[to_user],
        fail_silently=False
    )



