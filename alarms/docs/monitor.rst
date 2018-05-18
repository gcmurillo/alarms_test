

.. _monitor-model:

*************
Monitor Model
*************

   Monitor look for an or many objects. This objects can be selected directly in devices and variables fields, or
   writing a query with `Q Objects <https://docs.djangoproject.com/en/1.11/topics/db/queries/#complex-lookups-with-q-objects>`_
   Configuration of times and devices which are monitored to generated an Event

.. _monitor-fields:

Fields
------

   Here an explain about Monitor's Model fields:

   **devices** ``ManyToManyField``

   This field create a M2M relation with Devices objects, this field can be blank when Monitor Object is created

   **variables** ``ManyToManyField``

   This field create a M2M relation with Var objects, this field can be blank when Monitor Object is created

   **lookups** ``TextField``

   Here you can create a query with `Q Objects <https://docs.djangoproject.com/en/1.11/topics/db/queries/#complex-lookups-with-q-objects>`_.
   This query filter Var objects for evaluated it with Alarm's formula. This field is validated via `regexValidator <https://docs.djangoproject.com/en/1.11/ref/validators/#regexvalidator>`_.
   More about :ref:`create-functional-lookup`

   .. warning::
      In ``Monitor`` creation you should to choose only for ``device``, ``var`` or create a ``lookup``. One of them are required.

   **start_time** ``DateTimeField``

   Date when monitor is created or activated

   **duration** ``FloatField``

   If null, monitor never ends.

   **frequency** ``CharField``

   There are some frequency choices::

      DIARIO = 'D'
      SEMANAL = 'S'
      MENSUAL = 'M'
      ANUAL = 'A'

   This can be selected in Django Admin Site.

   **weight** ``IntegerField``

   Define Monitor's priority

   **active** ``BooleanField``

   *Default=True*, if is `False`, the monitor is not considered.

.. _create-functional-lookup:

How to create a functional lookup field?
----------------------------------------

   How we can see in **lookups** field definition above, we use `Q Objects <https://docs.djangoproject.com/en/1.11/topics/db/queries/#complex-lookups-with-q-objects>`_.
   The query created in this field, filter Var objects which eventually will be evaluated with Alarm formula field,
   for this reason we need to created an valid query.

   As query filter Vars, the Q objects should to be referenced to their fields, here some examples::

      Q(slug__startswith='alarms') & Q(device__profile__name='Feeder')

   In the example above, we get the Vars which ``slug`` contains `alarms` word, and is referenced with ``device`` with `Feeder` profile.
   Here another example::

      Q(slug__startswith='food') | Q(slug__startswith='voltaje')

   With the filter above we vars with `food` and `voltaje` in ``slug`` field.

   You can create a query with a single or many Q objects. To separate the Q objects, you can use ``&``, ``|``, or ``,``.
   For more information for Q objects, read the `docs <https://docs.djangoproject.com/en/1.11/topics/db/queries/#complex-lookups-with-q-objects>`_.

   .. warning::

      The Q objects are validated with `regexValidator <https://docs.djangoproject.com/en/1.11/ref/validators/#regexvalidator>`_,
      be careful to close all the parenthesis and brackets, and work with the corrects fields.
      Only the string format is validated. The correct execution of the query is not validated here.

