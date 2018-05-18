
.. _api/alarms/subscriptions:

************************
api/alarms/subscriptions
************************

   This endpoint return information for :ref:`subscription-model`. For this endpoint the enable operations are:
   ``GET``, ``DELETE``.

   To get the information, we use :ref:`subscription-serializer`. Here an example for ``GET`` request to ``api/alarms/subscription/``::

        [
            {
                "id": 1,
                "active": true,
                "created": "2018-04-20T18:42:10Z",
                "email": true,
                "staff_template": "email_template_staff.html",
                "user_template": null,
                "staff_template_text": "",
                "user_template_text": "",
                "user": 2,
                "group": null,
                "alarm": 22
            },
            {
                "id": 2,
                "active": true,
                "created": "2018-04-20T18:42:10Z",
                "email": true,
                "staff_template": "email_template_staff.html",
                "user_template": null,
                "staff_template_text": "",
                "user_template_text": "",
                "user": null,
                "group": 1,
                "alarm": 23
            }
        ]

   To get a single object in the API, we use ``pk`` to identify the object. We should put ``pk`` to ``api/alarms/notifications/<pk>/``.
   For example, if we want the object with ``pk=1``, then ``api/alarms/notifications/1/``, the output is::

        {
            "id": 1,
            "active": true,
            "created": "2018-04-20T18:42:10Z",
            "email": true,
            "staff_template": "email_template_staff.html",
            "user_template": null,
            "staff_template_text": "",
            "user_template_text": "",
            "user": 2,
            "group": null,
            "alarm": 22
        }

   To do ``PUT`` operation, only can change ``active`` field, user should have ``can_change_activition`` permission, for more information see
   Subscription :ref:`subscription-permissions`
