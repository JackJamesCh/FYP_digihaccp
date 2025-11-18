from django import forms
from .models import Deli, User, ChecklistTemplate, Checklist, ChecklistItem
from django.forms import inlineformset_factory

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


class ChecklistForm(forms.ModelForm):
    items_bulk = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "textarea textarea-bordered w-full h-40",
            "placeholder": "Paste food items here, one per line..."
        }),
        required=False,
        help_text="Enter one item per line. Example: Chicken Fillet Tray 1"
    )

    class Meta:
        model = Checklist
        fields = ["template", "deli", "frequency", "title"]



class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "order": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
        }


ChecklistItemFormSet = inlineformset_factory(
    Checklist,
    ChecklistItem,
    form=ChecklistItemForm,
    extra=3,     # number of blank items shown initially
    can_delete=False
)