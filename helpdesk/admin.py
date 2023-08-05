from django.contrib import admin
from .models import *


admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Ticket)
admin.site.register(Subcategory)
admin.site.register(Department)
admin.site.register(TelegramUser)
admin.site.register(Employee)


