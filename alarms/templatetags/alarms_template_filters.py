
from django.conf import settings
from django.apps import apps
from django import template
from django.utils import timezone
from django.template import Template, Context
from django.db.models import Q
VarLog = apps.get_model(settings.VARLOG_MODEL)

register = template.Library()


@register.filter(name='bit')
def bit(value, arg):

    """
    From a digit, convert into binary and return the digit in an index (arg)
    i.e:
    value = 32
    arg = 1
    value in binary = 100000, returning bit 1 -> 0
    :param value: var value
    :param arg: bit number
    :return: 1 or 0
    """
    binary = bin(value)[2:].zfill(int(arg) + 1)
    return int(binary[len(binary) - 1 - arg])


@register.filter('qs_filter')
def qs_filter(query, arg):

    """
    Getting a queryset and filter objects with lookups
    :param query: queryset
    :param arg: Lookups created with Q objects
    :return: List with filtered objects
    """
    log_ids = []
    for log in query:
        log_ids.append(log.pk)

    context = {'lookups': arg, 'log_ids': log_ids}  # i.e {'conditions': 'var.value > 5 and ...', 'stuff': [22,24,56]}
    template_text = "VarLog.objects.filter(Q(id__in={{ log_ids }}) & {{ lookups }})"

    template = Template(template_text)
    evaluated = eval(template.render(Context(context)))
    return evaluated