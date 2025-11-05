from django import forms
from django.contrib.auth import get_user_model
from .models import Ticket, TicketMessage

User = get_user_model()


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'name', 'last_name', 'email', 'department', 'company', 'contact_number',
            'due_date', 'nature_of_engagement', 'document_attached',
            'details_of_contracting_party', 'remarks'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nature_of_engagement': forms.Select(attrs={'class': 'form-control', 'id': 'nature-select'}),
            'document_attached': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'details_of_contracting_party': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Auto-fill user information if available
        if user:
            self.fields['name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def clean(self):
        cleaned_data = super().clean()
        nature_of_engagement = cleaned_data.get('nature_of_engagement')
        document_attached = cleaned_data.get('document_attached')
        details_of_contracting_party = cleaned_data.get('details_of_contracting_party')
        
        # For Review requests require document attachment
        if nature_of_engagement == 'for_review' and not document_attached:
            raise forms.ValidationError('Document attachment is required for review requests.')
        
        # For Review requests require contracting party details
        if nature_of_engagement == 'for_review' and not details_of_contracting_party:
            raise forms.ValidationError('Details of contracting party are required for review requests.')
        
        return cleaned_data


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'admin_comments', 'reviewed_document', 'assigned_to', 'priority']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'admin_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'reviewed_document': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show legal admins in assigned_to field
        self.fields['assigned_to'].queryset = User.objects.filter(role='admin')


class TicketFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Ticket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ChoiceField(
        choices=[('', 'All Departments')] + Ticket.DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company = forms.ChoiceField(
        choices=[('', 'All Companies')] + Ticket.COMPANY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nature_of_engagement = forms.ChoiceField(
        choices=[('', 'All Types')] + Ticket.NATURE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by ticket ID or user name'})
    )


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...'
            })
        }