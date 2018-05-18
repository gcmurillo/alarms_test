# coding=utf-8
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, RegexValidator
from gm2m import GM2MField


def get_unique_slug(model_instance, slugable_field_name, slug_field_name):

    """
    Takes a model instance, sluggable field name (such as 'title') of that
    model as string, slug field name (such as 'slug') of the model as string;
    returns a unique slug as string.
    """
    slug = slugify(getattr(model_instance, slugable_field_name))
    unique_slug = slug
    extension = 1
    ModelClass = model_instance.__class__

    while ModelClass._default_manager.filter(
            **{slug_field_name: unique_slug}
    ).exists():
        unique_slug = '{}-{}'.format(slug, extension)
        extension += 1

    return unique_slug


def validate_expression(str):

    """
    Validate in a string the () and [] incomplete
    """
    stack = []
    pushChars, popChars = "([", ")]"
    for c in str:
        if c in pushChars:
            stack.append(c)
        elif c in popChars:
            if not len(stack):
                raise ValidationError('La expresion tiene corchetes \'[ ]\' o parentesis \'( )\' sin cerrar')
            else:
                stackTop = stack.pop()
                balancingBracket = pushChars[popChars.index(c)]
                if stackTop != balancingBracket:
                    raise ValidationError('La expresion tiene corchetes \'[ ]\' o parentesis \'( )\' sin cerrar')

    if len(stack):
        raise ValidationError('La expresion tiene corchetes \'[ ]\' o parentesis \'( )\' sin cerrar')


class Monitor(models.Model):

    # frequency types
    DIARIO = 'D'
    SEMANAL = 'S'
    MENSUAL = 'M'
    ANUAL = 'A'

    FREQUENCY_CHOICES = (
        (DIARIO, 'Diario'),
        (MENSUAL, 'Mensual'),
        (SEMANAL, 'Semanal'),
        (ANUAL, 'Anual')
    )

    help_text_lookup = '''Valido para Q objects relacionado con variables. Ejemplo: Q(device__id__in=[1,2],
                            Q(value__gte=2) | Q(value__lte=0) .
                        Los Q objects podran estar separados por (,) , (|) o (&), dependiendo de la necesidad
                            y la complejidad del query. Dudas sobre el manejo de Q objects?
                            https://docs.djangoproject.com/en/1.11/topics/db/queries/#complex-lookups-with-q-objects
                              Debe seleccionar entre variables, devices o ingresar una sentencia en Lookups, solo una de ellas. '''

    regex = r"(^(\(*~?Q\([\w]+=[\w\[\],-_']+\)\)*\s?[,&\|]\s?)*\(*~?Q\([\w]+=[\w\[\],-_']+\)\)*)$"
    mensaje_error_lookup = '''Lookup Incorrecto, asegurese separar por (,), (&) o (|) cada Q object.
                            No dejar ningun caracter al final del ultimo Q object. '''

    devices = models.ManyToManyField(settings.DEVICE_MODEL, blank=True)
    variables = models.ManyToManyField(settings.VAR_MODEL, null=True, blank=True)
    lookups = models.TextField(max_length=255, null=True, blank=True, help_text=help_text_lookup,
                               validators=[RegexValidator(regex, message=mensaje_error_lookup), validate_expression])
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.FloatField(default=0, help_text='In hours') # duracion en horas
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES, default=DIARIO)
    weight = models.IntegerField(blank=True, default=0, null=True) # prioridad
    active = models.BooleanField(default=False)

    def __str__(self):
        return 'Monitor ' + str(self.pk)


class Alarm(models.Model):

    help_text_alarm = '''Por ejemplo: "{{ var.value }} < 5" |
                        Analizara la variable seleccionada, previamente por el monitor,
                        evaluara esta formula y entregara un valor Booleano. IMPORTANTE: DEVOLVER VALOR BOOLEANO
                        Puede usar el filtro bit para obtener un bit de un número, ejemplo: {{ var.value | bit:2 }} '''

    name = models.CharField(max_length=50, null=True)
    slug = models.SlugField(blank=True, max_length=80)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    formula = models.TextField(max_length=255, default='code', blank=True,
                               validators=[MaxLengthValidator(255),],
                               help_text=help_text_alarm)
    duration = models.FloatField(default=0, help_text='In hours.')  # duracion en horas
    description = models.CharField(max_length=255, default='default')  # template para la descripcion de la descripcion de AlarmEvent
    monitor = models.ManyToManyField(Monitor, default=None)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        if not self.name:
            self.name = 'Alarma' + str(self.pk)
        super(Alarm, self).save(*args, **kwargs)

    def get_monitors(self):
        return "\n".join(obj.__str__() for obj in self.monitor.all())

    def __str__(self):
        return self.slug

    class Meta:
        permissions = (
            ('can_subscribe', 'Can subscribe alarm'),
        )


class AlarmEvent(models.Model):
    # Alarm types

    USER = 'US'
    DEVICE = 'DV'
    NO_DEVICE = 'ND'

    ALARM_CHOICES = (
        (USER, 'User'),
        (DEVICE, 'Device'),
        (NO_DEVICE, 'No-Device')
    )

    alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE, null=True)
    alarm_type = models.CharField(max_length=2, choices=ALARM_CHOICES, default=USER)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    device = models.ForeignKey(settings.DEVICE_MODEL, on_delete=models.CASCADE, null=True)
    variables = models.ForeignKey(settings.VAR_MODEL, on_delete=models.CASCADE, null=True)
    content_type = GM2MField(blank=True)
    description = models.CharField(max_length=255, default='description', null=True)

    def get_contents_type(self):
        return "\n".join(obj.__str__() + '|' for obj in self.content_type.all())

    def __str__(self):
        return self.alarm_type + '-' + str(self.pk)


class Subscription(models.Model):

    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE, null=True)
    email = models.BooleanField(default=True)
    staff_template = models.CharField(max_length=50, null=True, blank=True)  # Template name from template folder
    user_template = models.CharField(max_length=50, null=True, blank=True)
    staff_template_text = models.TextField(null=True, blank=True)  # raw HTML
    user_template_text = models.TextField(null=True, blank=True)

    def clean(self):
        if self.user is None and self.group is None:
            raise ValidationError('User or Group are required')
        if self.user is not None and self.group is not None:
            raise ValidationError('Only user or only group')
        if self.staff_template is None and self.user_template is None\
                and self.staff_template_text == "" and self.user_template_text == "":
            raise ValidationError('Insert staff or user template filename or write a staff or user template')
        if self.staff_template is not None and self.user_template is not None:
            raise ValidationError('Insert only a template!')
        if self.staff_template is not None and self.staff_template_text != '':
            raise ValidationError('Insert only a template!')
        if self.staff_template is not None and self.user_template_text != '':
            raise ValidationError('Insert only a template!')
        if self.user_template is not None and self.staff_template_text != '':
            raise ValidationError('Insert only a template!')
        if self.user_template is not None and self.user_template_text != '':
            raise ValidationError('Insert only a template!')
        if self.staff_template_text != '' and self.user_template_text != '':
            raise ValidationError('Insert only a template!')

    def __str__(self):
        return 'Subscription ' + str(self.pk)

    class Meta:
        permissions = (
            ('can_change_activation', 'Can change activation'),
        )


class Notification(models.Model):

    # Cheked options
    CHECKED = 'checked'
    UNCHECKED = 'unchecked'

    CHECKED_CHOICES = (
        (CHECKED, 'Checked'),
        (UNCHECKED, 'Unchecked')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    event = models.ForeignKey(AlarmEvent, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default=UNCHECKED, choices=CHECKED_CHOICES, max_length=10)

    def __str__(self):
        return 'Notification ' + str(self.pk)
