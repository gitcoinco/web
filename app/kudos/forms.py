from django import forms


class KudosSearchForm(forms.Form):
    kudos_search = forms.CharField(label='Kudos Search', max_length=100)
