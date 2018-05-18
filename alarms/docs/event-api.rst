
.. _api/alarms/events:

*****************
api/alarms/events
*****************

   This endpoint return information for :ref:`alarm-event-model`. For this endpoint the enable operations are:
   ``GET``, ``DELETE``.

   To get the information, we use :ref:`alarm-event-serializer`. Here an example for ``GET`` request to ``api/alarms/events/``::

         [
                .
                .
                .
                {
                    "id": 3,
                    "content_type": [],
                    "alarm_type": "US",
                    "created": "2018-04-20T18:42:54.536830Z",
                    "finished": "2018-04-20T19:08:08.198542Z",
                    "description": "Poca comida en alimentadores",
                    "alarm": 22,
                    "device": 3,
                    "variables": 3
                },
                {
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
                {
                    "id": 6,
                    "content_type": [],
                    "alarm_type": "US",
                    "created": "2018-04-20T19:06:04.385906Z",
                    "finished": "2018-04-20T19:07:09.912253Z",
                    "description": "Poca comida en alimentadores",
                    "alarm": 22,
                    "device": 2,
                    "variables": 2
                },
                .
                .
                .
         ]

   To get a single object in the API, we use ``pk`` to identify the object. We should put ``pk`` to ``api/alarms/events/<pk>/``.
   For example, if we want the object with ``pk=5``, then ``api/alarms/events/5/``, the output is::

        {
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
        }

   As you can see, in ``content_type`` field are some different objects. For more information about ``content_type`` field, please visit
   :ref:`alarm-event-model` and :ref:`alarm-event-serializer`.

