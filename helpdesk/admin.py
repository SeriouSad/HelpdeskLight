from django.contrib import admin
from .models import *


admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Ticket)
admin.site.register(Subcategory)
admin.site.register(Departments)
admin.site.register(TelegramUser)

