from django import forms
from .models import Deli, User, ChecklistTemplate, Checklist, ChecklistItem
from django.forms import inlineformset_factory

# (Deli Form)
# I made this form so managers can easily create or edit deli information.
# Using a ModelForm saves me time since Django automatically builds the fields for me.
class DeliForm(forms.ModelForm):
    class Meta:
        model = Deli
        fields = ['deli_name', 'address', 'phone_number']
        # I added widgets so the form looks nicer in the HTML templates.
        widgets = {
            'deli_name': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter deli name'}),
            'address': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter address'}),
            'phone_number': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter phone number'}),
        }


# (Assign Deli Form)
# I created this form so managers can assign one user to multiple delis.
# I used a ModelMultipleChoiceField so they can select several delis at once.
class AssignDeliForm(forms.ModelForm):
    delis = forms.ModelMultipleChoiceField(
        queryset=Deli.objects.all(),  # Shows all delis for selection
        widget=forms.CheckboxSelectMultiple,  # I chose checkboxes because it's simpler for multiple choices
        required=False,
        label="Assign to Delis",
    )

    class Meta:
        model = User
        fields = ['delis']  # Only editing the delis connected to the user


# (Checklist Form)
# I created this form so managers can build a new checklist for a deli.
# I added an extra field `items_bulk` so they can paste multiple checklist items at once.
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
        # Django will build these fields for me based on the model


# (Checklist Item Form)
# This form is used when manually editing or adding individual checklist items.
# I added widgets so the input boxes match the styling of the rest of the site.
class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "order": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
        }


# (Checklist Item Formset)
# I created a formset so I can edit multiple checklist items on a single page.
# Django's inlineformset_factory lets me link the items directly to their parent checklist.
ChecklistItemFormSet = inlineformset_factory(
    Checklist,
    ChecklistItem,
    form=ChecklistItemForm,
    extra=3,     # I added 3 extra empty rows so managers can add items quickly
    can_delete=False  # I disabled delete here because I want edits handled separately
)
