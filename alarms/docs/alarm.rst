
.. _alarm-model:

***********
Alarm Model
***********

   Alarm raise some AlarmEvent if ``formula`` evaluation. In Alarms app, exists some :ref:`predefined-alarms` instances.

Fields
------

   Here an explain about Alarm's Model fields:

   **name** ``CharField``

   Set a name for the Alarm instance

   **slug** ``SlugField``

   Slug is automatically set with `prepopulated field <https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.ModelAdmin.prepopulated_fields>`_
   for Django admin.

   **creator** ``ForeignKey(User)``

   Set ``User`` who create Alarm.

   **formula** ``TextField``

   A formula is a `Django template <https://docs.djangoproject.com/en/1.11/topics/templates/>`_, for this reason you can use
   `Built-in filter <https://docs.djangoproject.com/en/1.11/ref/templates/builtins/#ref-templates-builtins-filters>`_. This formula
   will evaluate the vars filtered by ``lookups`` field from Monitor :ref:`monitor-fields`. More information about :ref:`create-alarm-formula`

   .. warning::
      The sentence should return some ``Boolean``.

   **duration** ``FloatField``

   Set how much time should wait to create another event and notification. The time is setting in hours.

   **description** ``CharField``

   Small description about the alarm.

   **monitor** ``ManyToManyKey``

   Many to many relation with a single or many Monitors objects (ref: :ref:`monitor-model`)

.. _alarm-permissions:

Permissions
-----------

   **can_subscribe**

   With this permission an User or Group can subscribe to an Alarm instance. For more information about Subscription, visit :ref:`subscription-model`

.. _predefined-alarms:

Predefined Alarms
-----------------

   Here is a table content of many Alarms that are predefined in the app


   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | Bit    | Alarma                     | Descripción                                                                                       |
   +========+============================+===================================================================================================+
   | 31     | Alimentación Máxima        | Cuando se supera alimentacion maxima diaria definida por el usuario                               |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 20     | Sensor 2 Alto              | Cuando el valor del sensor 2 es superior a un valor prefijado                                     |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 19     | Sensor 2 Bajo              | Cuando el valor del sensor 2 es inferior a un valor prefijado                                     |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 18     | Sensor 1 Alto              | Cuando el valor del sensor 1 es superior a un valor prefijado                                     |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 17     | Sensor 1 Bajo              | Cuando el valor del sensor 1 es inferior a un valor prefijado                                     |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 16     | Batería Alta               | Cuando el voltaje de la batería es superior a un valor prefijado                                  |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 15     | Batería Baja               | Cuando el voltaje de la batería es inferior a un valor prefijado                                  |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 14     | Hidrófono Desconectado     | Cuando no se detecta ruido                                                                        |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 13     | Sensor 2 Desconectado      | Sin consumo o muy bajo                                                                            |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 12     | Dosificador Obstruido      | Alto consumo                                                                                      |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 11     | Tolva Vacía                |                                                                                                   |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 10     | Dosificador Desconectado   | Sin consumo o muy bajo                                                                            |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 9      | Aspersor Obstrudo          | Alto consumo                                                                                      |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 8      | Aspersor Desconectado      | Sin consumo o muy bajo                                                                            |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 7      | Alimentación Deshabilitada | Cuando el equpo decide no alimentar, en otra variable se especifica un codigo indicando la causa  |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 6      | Luz Desconectada           |                                                                                                   |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 5      | Firmware con Errores       | Cuando el programa que llego para ser actualizado contine errores                                 |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 4      | Sensor 1 Desconectado      | Sin consumo o muy bajo                                                                            |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 3      | Sensor Temp. Desconectado  |                                                                                                   |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 2      | Equipo Iniciado            |                                                                                                   |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+
   | 1      | Shield Incompatible        | Cuando el equpo detecta que algun shield no es compatible con el software o hardware              |
   +--------+----------------------------+---------------------------------------------------------------------------------------------------+


.. _create-alarm-formula:

How create Alarm Formula field?
-------------------------------

   In ``formula`` field you should to use `Django template <https://docs.djangoproject.com/en/1.11/topics/templates/>`_.
   This formula evaluated Vars, filtered by Monitor. You can use `Built-in filter <https://docs.djangoproject.com/en/1.11/ref/templates/builtins/#ref-templates-builtins-filters>`_, or
   some Filters created for this app (Ref: :ref:`template-filters-tags`).

   Let see some examples::

      {{ var.value }} > 5

   The example above is the most simple case of ``formula``. In this case, it return ``True`` if the value of the evaluated var is greater than 5.
   You can use ``<``, ``!=``, ``is not``, ``in``, ``==``, ``>``, ``<=``, ``>=`` and more operators.

   In other example, we will use ``bit`` filter from :ref:`template-filters-tags`::

      {{ var.value | bit:1 }}

   This formula template is use in our :ref:`predefined-alarms`, and return 1 if the bit 1 in the value, converted in binary, is 1

   In other example, we can use ``qs_filter`` from :ref:`template-filters-tags`::

      {{ var.value }} < 5 and {{ var.varlog_set.all | dictsortreversed:'date' | slice:':2' | qs_filter:'Q(value__lt=5)' | length_is:'2' }}

   In the example we use some `Built-in filters <https://docs.djangoproject.com/en/1.11/ref/templates/builtins/#ref-templates-builtins-filters>`_ too.
   ``qs_filter`` get as argument a query created with `Q Objects <https://docs.djangoproject.com/en/1.11/topics/db/queries/#complex-lookups-with-q-objects>`_.
   As you can see the sentence return a ``Boolean``.

   **Remember, the sentence should return a ``Boolean``**