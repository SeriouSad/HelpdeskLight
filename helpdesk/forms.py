from django import forms
from .models import *


class NewTicket(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['category', 'subcategory', 'phone', 'place', 'email', 'description']


class EditTicketOperator(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'department', 'responsible', 'category', 'subcategory', 'phone', 'place', 'email', 'description']

        widgets = {
            'description': forms.Textarea(attrs={'readonly': True})
        }

class EditTicketUser(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['category', 'subcategory', 'phone', 'place', 'email', 'description']

    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        super(EditTicketUser, self).__init__(*args, **kwargs)
        if self.instance.status != 0:
            self.fields['description'].widget.attrs['readonly'] = True
            self.fields['category'].widget.attrs['disabled'] = True
            self.fields['subcategory'].widget.attrs['disabled'] = True
            self.fields['phone'].widget.attrs['readonly'] = True
            self.fields['place'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True


class NewTicketOperator(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'department', 'responsible', 'category', 'subcategory', 'phone', 'place', 'email', 'description']


class ChatForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

        # def __init__(self, *args, **kwargs):
        #     self.ticket_token = kwargs.pop('ticket_token', None)
        #     super(ChatForm, self).__init__(*args, **kwargs)






