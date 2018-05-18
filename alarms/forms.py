
from django import forms
from .models import Subscription, Monitor
from django.core.exceptions import ValidationError

class SubscriptionModelForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = ('active', 'user', 'group', 'alarm', 'email', 'staff_template', 'user_template')

class MonitorModelForm(forms.ModelForm):

    class Meta:
        model = Monitor
        fields = ('devices', 'variables', 'lookups', 'start_time', 'duration', 'frequency', 'weight', 'active')

    def clean(self):
        ''' Check if only is selected devices or variables,
            if both are selected raise an error message '''

        devices = self.cleaned_data.get('devices')
        variables = self.cleaned_data.get('variables')
        lookups = self.cleaned_data.get('lookups')
        if devices and variables and lookups:
            raise ValidationError('Only devices or only variables or only lookups')
        elif not devices and not variables and not lookups:
            raise ValidationError('Select devices or variables or lookups')
        elif not devices and variables and lookups:
            raise ValidationError('Only devices or only variables or only lookups')
        elif devices and variables and not lookups:
            raise ValidationError('Only devices or only variables or only lookups')
        elif devices and not variables and lookups:
            raise ValidationError('Only devices or only variables or only lookups')

        return self.cleaned_data
