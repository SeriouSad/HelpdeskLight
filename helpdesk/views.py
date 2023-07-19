from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from .models import *
from .serializers import *


class CreateUserTg(APIView):
    def post(self, request):
        data = dict(request.data)
        email = data.get("email", None)
        tg_id = data.get("tg_id", None)
        if email and tg_id:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create(email=email, username=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)
                confirmation_link = f"http://{current_site.domain}/helpdesk/confirm_email/{token}/{uid}/{tg_id}/"
                subject = 'Подтверждение адреса электронной почты'
                message = render_to_string('confirmation/email_confirmation.html',
                                           {'confirmation_link': confirmation_link})
                email = EmailMessage(subject, message, to=[email])
                email.content_subtype = 'html'
                email.send()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"Error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': 'Wrong fields'}, status=status.HTTP_400_BAD_REQUEST)


class CreateTicket(APIView):
    def post(self, request):
        data = dict(request.data)
        tg_id = data.get("tg_id")
        subcategory = data.get("subcategory")
        description = data.get("description")
        contacts = data.get("contacts")
        if tg_id and description and contacts:
            owner = TelegramUser.objects.get(tg_id=tg_id).user
            subcategory_obj = Subcategory.objects.get(id=subcategory)
            category = subcategory_obj.category
            ticket = Ticket.objects.create(owner=owner, contacts=contacts, category=category,
                                           subcategory=subcategory_obj, description=description)
            ticket.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Wrong fields'}, status=status.HTTP_400_BAD_REQUEST)


class GetTopics(APIView):
    def get(self, request):
        category_list = []
        category = list(Category.objects.all())
        for i in category:
            serializer = SubcategorySerializer(Subcategory.objects.filter(category=i), many=True)
            category_list.append({"id": i.id, "name": i.name, "subcategory": serializer.data})
        return Response(category_list, status=status.HTTP_200_OK)


class GetTicket(APIView):
    def get(self, request):
        tg_id = request.GET.get("tg_id")
        ticket_token = request.GET.get("token")
        if tg_id:
            if ticket_token:
                ticket = Ticket.objects.get(token=ticket_token)
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                owner = TelegramUser.objects.get(tg_id=tg_id).user
                tickets = Ticket.objects.filter(owner=owner)
                serializer = TicketSerializer(tickets, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Wrong fields'}, status=status.HTTP_400_BAD_REQUEST)


def confirm_email(request, uidb64, token, tg_id):
    try:
        tg_id = int(tg_id)
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_email_confirmed = True
            user.save()
            user_tg = TelegramUser.objects.create(tg_id=tg_id, user=user)

        return render(request, 'confirmation/email_confirmed.html')
    except User.DoesNotExist:
        return render(request, 'confirmation/invalid_confirmation_link.html')
