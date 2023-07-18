import datetime
import uuid
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings



class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Departments(models.Model):
    name = models.CharField(max_length=100, default="")
    location = models.CharField(max_length=100, default="")
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    tg_id = models.IntegerField(unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Ticket(models.Model):
    STATUS_CHOICES = (
        (0, 'Создан'),
        (1, 'В работе'),
        (-2, 'Отклонен'),
        (2, 'Ждет уточнения'),
        (3, 'Решен'),
        (-1, 'Отменен'),
    )
    PRIORITY = (
        (1, "Стандартная"),
        (2, "Высокая"),
        (3, "Экстренная")
    )

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    contacts = models.CharField(max_length=300, default="")
    from_mail = models.BooleanField(default=False, blank=True)
    email = models.CharField(default="", max_length=100, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, blank=True, default=0)
    priority = models.IntegerField(choices=PRIORITY, blank=True, default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=False)
    deadline_date = models.DateField(blank=False, default=datetime.date.today() + datetime.timedelta(days=3))
    department = models.ForeignKey(Departments, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'code: {self.token} - date: {self.created}'


class Comment(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='comments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField(
        verbose_name='content', blank=False, help_text=".")

    def __str__(self):
        return f'from {self.owner} on ticket #{self.ticket.code}'


@receiver(pre_save, sender=Ticket)
def generate_token(sender, instance, **kwargs):
    if not instance.token:
        instance.token = uuid.uuid4()