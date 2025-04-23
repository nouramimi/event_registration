# forms.py

from django import forms
from .models import Event, Registration

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date', 
                 'location', 'capacity', 'category', 'image', 'is_published']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
            
        return cleaned_data

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = []  # We'll set event and user in the view
        
    # Additional fields could be added here if needed
    # For example, for collecting additional info during registration
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Additional Notes'
    )