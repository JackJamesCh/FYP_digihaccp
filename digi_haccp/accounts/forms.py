from django import forms
from .models import Deli, User

# Simple form to create or edit deli entries
class DeliForm(forms.ModelForm):
    class Meta:
        model = Deli
        fields = ['deli_name', 'address', 'phone_number']
        widgets = {
            'deli_name': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter deli name'}),
            'address': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter address'}),
            'phone_number': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter phone number'}),
        }


class AssignDeliForm(forms.ModelForm):
    delis = forms.ModelMultipleChoiceField(
        queryset=Deli.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign to Delis",
    )

    class Meta:
        model = User
        fields = ['delis']

