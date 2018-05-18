
from rest_framework import serializers
from .models import Device, Var


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'


class VarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Var
        fields = '__all__'