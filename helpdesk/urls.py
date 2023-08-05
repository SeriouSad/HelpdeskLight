from django.urls import path
from . import views

urlpatterns = [
    path("api/create-usertg", views.CreateUserTg.as_view()),
    path("api/create-ticket", views.CreateTicket.as_view()),
    path("api/topics", views.GetTopics.as_view()),
    path("api/ticket", views.GetTicket.as_view()),
    path("api/check-user", views.CheckUser.as_view()),
    path('confirm_email/<str:token>/<str:uidb64>/<str:tg_id>/', views.confirm_email, name='confirm_email'),
    path('', views.index, name='index'),
    path('create-new', views.create_new, name='create_new'),
    path('sort-tickets', views.ticket_sort, name='ticket_work'),
    path('sort-tickets/<int:ticket_id>', views.ticket_sort, name='ticket_work2'),
    path('my-tickets', views.user_tickets, name='my_tickets'),
    path('my-tickets/<int:ticket_id>', views.user_tickets, name='my_tickets2'),
    path('do-tickets', views.do_tickets, name='do_tickets'),
    path('do-tickets/<int:ticket_id>', views.do_tickets, name='do_tickets2')
]