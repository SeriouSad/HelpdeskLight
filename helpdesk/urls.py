from django.urls import path
from .views import *

urlpatterns = [
    path("api/create-usertg", CreateUserTg.as_view()),
    path("api/create-ticket", CreateTicket.as_view()),
    path("api/topics", GetTopics.as_view()),
    path("api/ticket", GetTicket.as_view()),
    path("api/check-user", CheckUser.as_view()),
    path('confirm_email/<str:token>/<str:uidb64>/<str:tg_id>/', EmailConfirmationView.as_view(), name='confirm_email'),
    path('', IndexView.as_view(), name='index'),
    path('create-new', create_new, name='create_new'),
    path('sort-tickets', ticket_sort, name='ticket_work'),
    path('sort-tickets/<int:ticket_id>', ticket_sort, name='ticket_work2'),
    path('my-tickets', user_tickets, name='my_tickets'),
    path('my-tickets/<int:ticket_id>', user_tickets, name='my_tickets2'),
    path('do-tickets', do_tickets, name='do_tickets'),
    path('do-tickets/<int:ticket_id>', do_tickets, name='do_tickets2')
]