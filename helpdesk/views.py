from django.http import Http404
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import *
from .serializers import *
from .forms import *


# region API
class CreateUserTg(APIView):
    def post(self, request):
        data = dict(request.data)
        email = data.get("email", None).lower()
        tg_id = data.get("tg_id", None)
        if email and tg_id:
            if not TelegramUser.objects.filter(tg_id=tg_id).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create(email=email, username=email)
                else:
                    user = User.objects.get(email=email)
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
                return Response({"Error": "TG user already exists"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'Error': 'Wrong fields'}, status=status.HTTP_400_BAD_REQUEST)


class CheckUser(APIView):
    def get(self, request):
        data = dict(request.data)
        tg_id = int(data.get("tg_id", None))
        if tg_id:
            if TelegramUser.objects.filter(tg_id=tg_id).exists():
                return Response({"confirmed": True}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'Error': 'Wrong fields'}, status=status.HTTP_400_BAD_REQUEST)


class CreateTicket(APIView):
    def post(self, request):
        data = dict(request.data)
        tg_id = data.get("tg_id")
        subcategory = data.get("subcategory")
        description = data.get("description")
        contacts = data.get("contacts")
        place = data.get("place")
        if tg_id and description and contacts:
            owner = TelegramUser.objects.get(tg_id=tg_id).user
            subcategory_obj = Subcategory.objects.get(id=subcategory)
            category = subcategory_obj.category
            ticket = Ticket.objects.create(owner=owner, phone=contacts, category=category,
                                           subcategory=subcategory_obj, description=description, place=place, type=2)
            ticket.save()
            return Response(ticket.token, status=status.HTTP_200_OK)
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


# endregion
class EmailConfirmationView(View):
    @staticmethod
    def get(request, uidb64, token, tg_id):
        try:
            tg_id = int(tg_id)
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_email_confirmed = True
                user.save()
                user_tg = TelegramUser.objects.create(tg_id=tg_id, user=user)
                user_tg.save()

            return render(request, 'confirmation/email_confirmed.html')
        except User.DoesNotExist:
            return render(request, 'confirmation/invalid_confirmation_link.html')


# TODO Переделать функцию на этот вью
class SendMessageView(View):
    @staticmethod
    def post(request, ticket):
        message_form = ChatForm(request.POST)
        if message_form.is_valid():
            message_form.instance.owner = request.user
            message_form.instance.ticket = ticket
            message_form.save()
            return True


def send_message(request, ticket):
    if request.method == 'POST':  # Сохраняем сообщение только при POST запросе
        message_form = ChatForm(request.POST)
        if message_form.is_valid():
            message_form.instance.owner = request.user
            message_form.instance.ticket = ticket
            message_form.save()
            return True


class IndexView(View):
    @staticmethod
    @login_required
    def get(request):
        return render(request, 'index.html', {'user': request.user})


class CreateNewTicketView(View):
    @staticmethod
    @login_required
    def get(request):
        if request.user.groups.filter(name__in=["Employee", "Operators"]):
            form = NewTicketOperator()
        else:
            form = NewTicket()
        return render(request, 'create_ticket.html', {'form': form, 'user': request.user})

    @staticmethod
    @login_required
    def post(request):
        if request.user.groups.filter(name__in=["Employee", "Operators"]):
            form = NewTicketOperator(request.POST)
        else:
            form = NewTicket(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            return render(request, 'index.html', {'user': request.user})



@login_required
def create_new(request):
    if request.method == 'POST':
        if request.user.groups.filter(name__in=["Employee", "Operators"]):
            form = NewTicketOperator(request.POST)
        else:
            form = NewTicket(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            return render(request, 'index.html', {'user': request.user})
    if request.user.groups.filter(name__in=["Employee", "Operators"]):
        form = NewTicketOperator()
    else:
        form = NewTicket()
    return render(request, 'create_ticket.html', {'form': form, 'user': request.user})


@login_required
def ticket_sort(request, ticket_id=None):
    link = "ticket_work2"
    tickets = Ticket.objects.filter(status=0)
    if ticket_id:
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        chat_form = ChatForm()
        if request.method == 'POST':
            if send_message(request, ticket):
                url = reverse(link, args=[ticket.id])
                return redirect(url)

            form = EditTicketOperator(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
            else:
                form = EditTicketOperator(instance=ticket)
            messages = Comment.objects.filter(ticket=ticket)

            return render(request, 'employee/ticket_work.html',
                          {"tickets": tickets, 'form': form, 'link': link,
                           'messages': messages, 'chat': True, "chat_form": chat_form, 'user': request.user})
        else:
            messages = Comment.objects.filter(ticket=ticket)
            form = EditTicketOperator(instance=ticket)
            return render(request, 'employee/ticket_work.html',
                          {"tickets": tickets, 'form': form, 'link': link,
                           'messages': messages, 'chat': True, "chat_form": chat_form, 'user': request.user})
    return render(request, 'employee/ticket_work.html',
                  {"tickets": tickets, 'form': None, 'link': link, 'user': request.user})


@login_required
def user_tickets(request, ticket_id=None):
    tickets = Ticket.objects.filter(owner=request.user)
    link = "my_tickets2"
    if ticket_id:
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        chat_form = ChatForm()
        if request.method == 'POST':
            if send_message(request, ticket):
                url = reverse(link, args=[ticket.id])
                return redirect(url)

            form = EditTicketUser(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
            else:
                form = EditTicketUser(instance=ticket)
            messages = Comment.objects.filter(ticket=ticket)

            return render(request, 'employee/ticket_work.html',
                          {"tickets": tickets, 'form': form, 'link': link,
                           'messages': messages, 'chat': True, "chat_form": chat_form, 'user': request.user})
        else:
            messages = Comment.objects.filter(ticket=ticket)
            form = EditTicketUser(instance=ticket)
            return render(request, 'employee/ticket_work.html',
                          {"tickets": tickets, 'form': form, 'link': link,
                           'messages': messages, 'chat': True, "chat_form": chat_form, 'user': request.user})
    return render(request, 'employee/ticket_work.html',
                  {"tickets": tickets, 'form': None, 'link': link, 'user': request.user})


@login_required
def do_tickets(request, ticket_id=None):
    link = "do_tickets2"
    if request.user.groups.filter(name__in=["Employee", "Operators"]):
        responsible = Employee.objects.get(user=request.user)
        tickets = Ticket.objects.filter(status__in=[1, 2], responsible=responsible)
    else:
        raise PermissionDenied()
    if ticket_id:
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        chat_form = ChatForm()
        if request.method == 'POST':
            if send_message(request, ticket):
                url = reverse(link, args=[ticket.id])
                return redirect(url)

            form = EditTicketOperator(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
            else:
                form = EditTicketOperator(instance=ticket)
            messages = Comment.objects.filter(ticket=ticket)

            return render(request, 'employee/ticket_work.html',
                          {"tickets": tickets, 'form': form, 'link': link,
                           'messages': messages, 'chat': True, "chat_form": chat_form, 'user': request.user})
        else:
            messages = Comment.objects.filter(ticket=ticket)
            form = EditTicketOperator(instance=ticket)
            return render(request, 'employee/ticket_work.html',
                          {"tickets": tickets, 'form': form, 'link': link,
                           'messages': messages, 'chat': True, "chat_form": chat_form, 'user': request.user})
    return render(request, 'employee/ticket_work.html',
                  {"tickets": tickets, 'form': None, 'link': link, 'user': request.user})
