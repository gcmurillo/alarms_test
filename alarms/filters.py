import django_filters
from .models import Subscription, Notification, AlarmEvent
from django.contrib.auth.models import Group, User
from django import forms
from django.utils import timezone
from django.apps import apps
from django.db.models import Q

Device = apps.get_model('fotuto_models', 'Device') # importando modelo de aplicacion SOLO PARA PRUEBA, IMPORTANTE importar modelo real

BOOLEAN_CHOICES = (
    ('true', True),
    ('false', False)
)

class SubscriptionFilter(django_filters.FilterSet):

    ''' Filter class for Subscription APIView '''
    group__user = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Subscription
        fields = {
            'user':['exact'],
            'group__user': ['in']
        }


class NotificationFilter(django_filters.FilterSet):

    ''' Filter class for Notification APIView '''
    event__created = django_filters.DateTimeFromToRangeFilter(
                                widget=django_filters.widgets.RangeWidget(attrs={'placeholder': 'YYYY/MM/DD HH:MM:SS'}))

    class Meta:
        model = Notification
        fields = ['user_id', 'status', 'event__created']

class AlarmEventFilter(django_filters.FilterSet):

    ''' Filter class for AlarmEvent APIView '''

    def finished_function(self, queryset, name, value): # Filter Alarms, if finisg == True (2), get objects with lower date

        try:
            finished = self.request.query_params.get('finished', None)
            if finished is not None:
                if finished == '2':
                    return queryset.filter(finished__lte=timezone.now())
                elif finished == '3':
                    return queryset.filter(Q(finished__gte=timezone.now()) | Q(finished=None))
                else:
                    return queryset
        except:
            queryset = {}

        return queryset

    device_id = django_filters.ModelMultipleChoiceFilter(queryset=Device.objects.all(), widget=forms.CheckboxSelectMultiple)
    finished = django_filters.BooleanFilter(name='finished', method='finished_function')

    class Meta:
        model = AlarmEvent
        fields = {
            'device__network': ['in'],
        }
