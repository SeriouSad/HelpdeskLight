from django_mailbox.models import Mailbox, Message, EmailMessage
from ..models import Ticket, Comment
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.conf import settings
import base64
import re


def split_answer(message_text):
    lines = message_text.splitlines()
    index = next(i for i, x in enumerate(lines) if "IThelp@rea.ru" in x)
    response_text = '\n'.join(lines[:index])
    lines = [line for line in response_text.splitlines() if "Ответ на письмо" not in line]
    response_text = "\n".join(lines)
    response_text = "\n".join(line for line in response_text.splitlines() if line.strip())
    return response_text


def process_received_mail():
    mailbox = Mailbox.objects.get(name='IT-Help')

    for message in mailbox.get_new_mail():
        if re.fullmatch("\S*@rea.ru", message.from_address[0]):
            subject = message.subject
            text = message.text
            if not text:
                text = strip_tags(message.html)
                text = "\n".join(line for line in text.splitlines() if line.strip())
                text = re.sub(r'&nbsp;', '', text)
            from_user = message.from_address
            pattern = r'#(\d+)'
            match = re.findall(pattern, subject)
            if match:
                token = match[0]
                text = split_answer(text)
                ticket = Ticket.objects.get(token=token)
                Comment.objects.create(owner=ticket.owner, ticket=ticket, content=text)
            else:
                if not User.objects.filter(email=from_user).exists():
                    user = User.objects.create(email=from_user[0], username=from_user[0].split("@")[0])
                    message_text = render_to_string('email/new_account.html',
                                                    context={'username': user.username, 'password': 1234})
                    email = EmailMessage(f'Регистрация в системе', message_text, to=from_user)
                    email.content_subtype = 'html'
                    email.send()
                else:
                    user = User.objects.get(email=from_user[0])
                ticket = Ticket.objects.create(owner=user, description=text, email=from_user[0], type=1)
                message_text = render_to_string('email/new.html', context={'token': ticket.token})
                email = EmailMessage(f'#{ticket.token} | Заявка: {subject}', message_text, to=from_user)
                email.content_subtype = 'html'
                email.send()






