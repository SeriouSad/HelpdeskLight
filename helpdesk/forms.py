from django import forms
from .models import *

class NewTicket(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('category', 'subcategory', 'phone', 'place', 'email', 'description')