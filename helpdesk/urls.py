from django.urls import path
from . import views

urlpatterns = [
    path("api/createusertg", views.CreateUserTg.as_view()),
    path("api/createticket", views.CreateTicket.as_view()),
    path("api/topics", views.GetTopics.as_view()),
    path("api/ticket", views.GetTicket.as_view()),
    path('confirm_email/<str:token>/<str:uidb64>/<str:tg_id>/', views.confirm_email, name='confirm_email'),
]