
.. _subscription-model:

******************
Subscription Model
******************

   A ``Subscription`` help to create notifications and send emails to an ``User`` or ``Group`` whose are subscribed to an ``alarm``
   If an ``User`` or ``Group`` want to subscribe, they should have ``can_subscribe`` permission (ref: :ref:`alarm-permissions`)

Fields
------

   Here an explain about Alarm's Model fields:

   **active** ``BooleanField``

   If ``True``, the notifications and emails can be send. If ``False``, subscription doesn't work.

   **user** ``ForeignKey``

   Set the user who is subscribed to the alarm. Single user. **Should have permission**.

   **group** ``ForeignKey``

   Set the group who is subscribed to the alarm. **Should have permission**.

   **created** ``DateTimeField``

   Set date when the subscription is created.

   **alarm** ``ForeignKey``

   Set ``alarm`` that ``user`` or ``group`` are subscribed

   **email** ``BooleanField``

   If ``True``, when an event of the ``alarm`` is raise, an email is send to the ``user`` or ``group``

   **staff_template** ``CharField``

   Name of the template, from ``template folder``. Used in emails.

   **user_template** ``CharField``

   Name of the template, from ``template folder``. Used in emails.

   **staff_template_text** ``TextField``

   Can create a template directly in the ``TextArea``

   **user_template_text** ``TextField``

   Can create a template directly in the ``TextArea``

.. _subscription-permissions:

Permissions
-----------

   **can_change_activation**

   With this permission an User can change ``active`` field.