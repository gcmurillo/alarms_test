
.. _serializers:

***********
Serializers
***********

    This serializers use `Serializer class from DRF <http://www.django-rest-framework.org/api-guide/serializers/>`_

.. _monitor-serializer:

Monitor Serializer
------------------

    Get the data from all the fields from a Monitor Object (ref: :ref:`monitor-model`), using::

        class MonitorSerializer(serializers.ModelSerializer):
            class Meta:
                model = Monitor
                fields = '__all__'

.. _alarm-serializer:

Alarm Serializer
----------------

    Get the data from all the fields from a Alarms Object (ref: :ref:`alarm-model`), using::

        class AlarmSerializer(serializers.ModelSerializer):
            monitor = MonitorSerializer(many=True, read_only=True)

            class Meta:
                model = Alarm
                fields = '__all__'

    The ``monitor`` field of Alarm show all the data of it, using :ref:`monitor-serializer`, this information is ``read_only``

.. _alarm-event-serializer:

AlarmEvent Serializer
---------------------

    Get the data from all the fields from a AlarmEvent Object (ref: :ref:`alarm-event-model`), using::

        class AlarmEventSerializer(serializers.ModelSerializer):
            content_type = ContentTypeSerializer(many=True, read_only=True)

            class Meta:
                model = AlarmEvent
                fields = '__all__'

    As you can see, ``content_type`` field use a ``ContentTypeSerializer``, it uses this::

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

    **Remember**: :ref:`alarm-event-model` use `django-gm2m <http://django-gm2m.readthedocs.io/en/stable/>`_ for his ``content_type`` field,
    for this reason ``GenericSerializer`` should to serialize the data for any other model. You can see the rendered information in :ref:`alarm-event-api`

.. _subscription-serializer:

Subscription Serializer
-----------------------

    Get the data from all the fields from a Subscription Object (ref: :ref:`subscription-model`), using::

        class SubscriptionSerializer(serializers.ModelSerializer):
            class Meta:
                model = Subscription
                fields = '__all__'

.. _notification-serializer:

Notification Serializer
-----------------------

    Get the data from all the fields from a Notification Object (ref: :ref:`notification-model`), using::

        class NotificationSerializer(serializers.ModelSerializer):
            event = AlarmEventSerializer(read_only=True)

            class Meta:
                model = Notification
                fields = '__all__'

    The ``event`` field of Notification show all the data of it, using: :ref:`alarm-event-serializer`, this information is ``read_only``