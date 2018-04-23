from django import forms
from django.contrib import admin

from .models import Organization


class OrganizationAdminForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'


class OrganizationAdmin(admin.ModelAdmin):
    form = OrganizationAdminForm
    list_display = ['name', 'slug', 'created_on', 'modified_on', 'description']
    readonly_fields = [
        'name', 'slug', 'created_on', 'modified_on', 'description'
    ]


admin.site.register(Organization, OrganizationAdmin)
