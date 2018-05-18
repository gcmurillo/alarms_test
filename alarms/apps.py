from django.apps import AppConfig


class AlarmsModuloConfig(AppConfig):
    name = 'alarms'

    def ready(self):
        import alarms.signals