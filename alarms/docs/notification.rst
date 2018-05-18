
.. _notification-model:

******************
Notification Model
******************

   Notification model register the creation of events, referenced to an ``alarm`` and an ``user`` subscribed to it

Fields
------

   Here an explain about Alarm's Model fields:

   **user** ``ForeignKey``

   Set ``user`` subscribed to the ``alarm`` (ref: :ref:`alarm-model`) which create the ``event``.

   **event** ``ForeignKey``

   Set ``event`` which create notification (ref: :ref:`alarm-event-model`).

   **created**  ``DateTimeField``

   Set ``notification`` creation date automatically.

   **status** ``CharField``

   There is two *status* options::

      CHECKED = 'checked'
      UNCHECKED = 'unchecked'

