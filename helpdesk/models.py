import datetime
import uuid
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, default="")
    location = models.CharField(max_length=100, default="")
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    # Добавьте другие поля для сотрудника

    def __str__(self):
        return self.user.username


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
    APPEAL_TYPE = (
        (1, "Электронная почта"),
        (2, "Чат telegram"),
        (3, "Сайт"),
        (4, "Бот telegram"),
        (5, "Телефон"),
    )

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    type = models.IntegerField(choices=APPEAL_TYPE, blank=True, default=3)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=300, default="")
    place = models.CharField(max_length=300, default="")
    email = models.CharField(default="", max_length=100, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, blank=True, default=0)
    priority = models.IntegerField(choices=PRIORITY, blank=True, default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=False)
    deadline_date = models.DateField(blank=False, default=datetime.date.today() + datetime.timedelta(days=3))
    department = models.ManyToManyField(Department, null=True, blank=True)
    responsible = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)


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


@receiver(pre_save, sender=Ticket)
def handle_field_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_obj = Ticket.objects.get(pk=instance.pk)
            if instance.status != old_obj.status:
                #TODO Уведомления в телеграм
                pass

        except Ticket.DoesNotExist:
            pass

@receiver(pre_save, sender=Ticket)
def handle_field_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_obj = Ticket.objects.get(pk=instance.pk)
            if instance.responsible != old_obj.responsible:
                #TODO Уведомления в телеграм
                print("Тест")
                pass

        except Ticket.DoesNotExist:
            pass