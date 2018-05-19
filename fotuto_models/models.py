from django.db import models
# Create your models here.
# Modelos  creados para realizar pruebas del modulo de alarmas

# Var types

FOOD = 'food'
VOLTAJE = 'voltaje'
PRESION = 'presion'
ALARMS = 'api_alarms'

VARIABLES_TYPES = (
    (FOOD, 'Food'),
    (VOLTAJE, 'Voltaje'),
    (PRESION, 'Presion'),
    (ALARMS, 'Alarms')
)

ALIMENTADOR = 'AL'
FEEDER = 'FE'
AIRADOR = 'AR'
REPETIDORA = 'RP'
PROFILES = (
    (FEEDER, 'Feeder'),
)


class Profile(models.Model):
    profile_type = models.CharField(choices=PROFILES, default=FEEDER, max_length=20)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=80, blank=True)

    def __str__(self):
        return self.name


class Device(models.Model):
    serial = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    connected = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name + '-' + self.serial


class Var(models.Model):
    var_type = models.CharField(choices=VARIABLES_TYPES, default=VOLTAJE, max_length=15)
    name = models.CharField(max_length=80, blank=True)
    slug = models.SlugField(max_length=80, blank=True)
    value = models.IntegerField(default=0)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.slug


class Network(models.Model):
    name = models.CharField(max_length=50)
    devices = models.ManyToManyField(Device, null=True)

    def __str__(self):
        return self.name


class VarLog(models.Model):
    var = models.ForeignKey(Var, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.var.__str__() + '-' + str(self.pk)