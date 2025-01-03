# merchants/forms.py

from django import forms
from .models import MenuItem

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'
            }),
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'
            })
        }

from .models import Merchant

# merchants/forms.py
from django import forms
from .models import Merchant

class MerchantForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = ['name', 'description', 'image', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors',
                'placeholder': 'Enter your store name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors',
                'placeholder': 'Describe your store...',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'data-preview': 'preview-image'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'h-4 w-4 text-secondary border-gray-300 rounded focus:ring-secondary'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
        return image

class MerchantRegistrationForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = ['name', 'description', 'image', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-secondary focus:ring-secondary sm:text-sm',
                'placeholder': 'Enter your store name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-secondary focus:ring-secondary sm:text-sm',
                'placeholder': 'Describe your store and what makes it special'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'h-4 w-4 text-secondary focus:ring-secondary border-gray-300 rounded'
            })
        }