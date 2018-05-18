
.. _alarm-event-model:

*****************
Alarm Event Model
*****************

   The events are created only when an Alarm (ref: :ref:`alarm-model`) is raise. In Django Admin Site the events can be created or modified.

Fields
------

   Here an explain about AlarmEvent's Model fields:

   **alarm** ``ForeignKey``

   Set the ``Alarm`` who raise and create the alarm.

   **alarm_type** ``CharField``

   There are some types::

      USER = 'US'
      DEVICE = 'DV'
      NO_DEVICE = 'ND'

   This can be selected in Admin Site.

   **created** ``DateTimeField``

   Set the event creation date.

   **finished** ``DateTimeField``

   This field is automatically.

   **device** ``ForeignKey``

   Set the device which create event

   **variables** ``ForeignKey``

   Set the var which create event

   **content_type** ``GM2MField``

   Set some objects that can not be Device or Var necessarily. In this field we use `django-gm2m <http://django-gm2m.readthedocs.io/en/stable/>`_ app.
   With that app, we can create Generic M2M relations.

   **description** ``CharField``

   Small description for the Monitor

