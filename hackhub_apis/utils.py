import re
from .tokens import email_verification_token
from django.utils.http import urlsafe_base64_encode
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

def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_link = 'http://127.0.0.1:8000/auth/verify/email/' #Endpoint which will be called from frontend through POST API call with uid and token

    subject = "Verify Email"
    message = f"Hii {user.username},\nPlease Verify your email by clicking below link:\n{verification_link}\n uidb64 = {uid}\n Token={token}" #Added token and uidb64 externally just for now to testing, will remove when integrating with fronend
    to_user = user.email

    send_mail(
        subject,
        message,
        from_email= EMAIL_HOST_USER,
        recipient_list=[to_user],
        fail_silently=False
    )

def abuse_detector(title,content,chat_session):
    question_to_ask = "Detect the abusive or vulgur words in above text. Give message containing only abusive or vulgur words with all letters in lower case no other things and if no abusive text then just send OK"
    message = title + " " + content + '\n' + question_to_ask

    response = chat_session.send_message(message)

    abusive_words = response.text.split()

    if(response == "OK"):
        return []
    
    return abusive_words



