
from rest_framework import serializers
from .models import Monitor, Alarm, AlarmEvent, Subscription, Notification
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class GenericSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):

    '''
    Objects with using Related relationship.
    This serializer is used in AlarmEventSerializer, to get more information about objects in it,
    '''

    def to_representation(self, value):
        content = ContentType.objects.get_for_model(type(value), for_concrete_model=True)  # getting contentType of object
        dic = {
            "app_label": content.app_label,
            "model": content.model,
        }
        content_object = apps.get_model(content.app_label, content.model)  # getting object model
        generic_serializer = GenericSerializer(value)
        generic_serializer.Meta.model = content_object
        dic['data'] = generic_serializer.data

        return dic


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = '__all__'


class AlarmSerializer(serializers.ModelSerializer):
    monitor = MonitorSerializer(many=True, read_only=True)

    class Meta:
        model = Alarm
        fields = '__all__'


class AlarmEventSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(many=True, read_only=True)

    class Meta:
        model = AlarmEvent
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    event = AlarmEventSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'