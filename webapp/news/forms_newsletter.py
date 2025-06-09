from django.forms import ModelForm, EmailInput
from .models_newsletter import Newsletter

class NewsletterForm(ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter your email',
                'type': 'email',
                'required': True,
            }),
        }
