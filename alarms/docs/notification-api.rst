
.. _api/alarms/notifications:

************************
api/alarms/notifications
************************

   This endpoint return information for :ref:`notification-model`. For this endpoint the enable operations are:
   ``GET``, ``POST``, ``PUT``, ``DELETE``.

   To get the information, we use :ref:`notification-serializer`. Here an example for ``GET`` request to ``api/alarms/notifications/``::

        [
            {
                "id": 1,
                "event": {
                    "id": 1,
                    "content_type": [],
                    "alarm_type": "US",
                    "created": "2018-04-20T18:42:48.601020Z",
                    "finished": "2018-04-20T19:07:09.900468Z",
                    "description": "Poca comida en alimentadores",
                    "alarm": 22,
                    "device": 1,
                    "variables": 1
                },
                "created": "2018-04-20T18:42:48.613262Z",
                "status": "unchecked",
                "user": 2
            },
            {
                "id": 2,
                "event": {
                    "id": 2,
                    "content_type": [],
                    "alarm_type": "US",
                    "created": "2018-04-20T18:42:51.992901Z",
                    "finished": "2018-04-20T19:07:09.912253Z",
                    "description": "Poca comida en alimentadores",
                    "alarm": 22,
                    "device": 2,
                    "variables": 2
                },
                "created": "2018-04-20T18:42:52.003274Z",
                "status": "unchecked",
                "user": 2
            },
            .
            .
            .
        ]

   As can see, ``event`` field show all the data. Here more information about :ref:`notification-serializer`

   To get a single object in the API, we use ``pk`` to identify the object. We should put ``pk`` to ``api/alarms/notifications/<pk>/``.
   For example, if we want the object with ``pk=5``, then ``api/alarms/notifications/5/``, the output is::

        {
            "id": 5,
            "event": {
                "id": 5,
                "content_type": [
                    {
                        "app_label": "alarms",
                        "model": "monitor",
                        "data": {
                            "id": 3,
                            "lookups": "Q(device__profile__name='Feeder') & Q(slug__startswith='voltaje')",
                            "start_time": "2018-04-20T18:42:10Z",
                            "duration": 0.0,
                            "frequency": "D",
                            "weight": 0,
                            "active": true,
                            "devices": [],
                            "variables": []
                        }
                    },
                    {
                        "app_label": "fotuto_models",
                        "model": "device",
                        "data": {
                            "id": 2,
                            "serial": "AL2",
                            "name": "Alimentador2",
                            "connected": true,
                            "profile": 1
                        }
                    }
                ],
                "alarm_type": "US",
                "created": "2018-04-20T19:06:01.661641Z",
                "finished": "2018-04-20T19:07:09.900468Z",
                "description": "Poca comida en alimentadores",
                "alarm": 22,
                "device": 1,
                "variables": 1
            },
            "created": "2018-04-20T19:06:01.672946Z",
            "status": "unchecked",
            "user": 2
        }

   Can do ``DELETE``, ``PUT`` and ``POST`` operations. You can only change ``status`` field.