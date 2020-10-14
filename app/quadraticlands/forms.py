from django import forms


class ClaimForm(forms.Form):
    user_sig = forms.CharField(label='Signature ', max_length=100)
