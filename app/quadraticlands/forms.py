from django import forms


class ClaimForm(forms.Form):
    your_name = forms.CharField(label='Signature ', max_length=100)
