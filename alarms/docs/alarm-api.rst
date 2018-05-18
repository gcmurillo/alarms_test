
.. _api/alarms:

**********
api/alarms
**********

   This endpoint return information for :ref:`alarm-model`. For this endpoint the enable operations are:
   ``GET``, ``POST``, ``PUT``, ``DELETE``.

   To get the information, we use :ref:`alarm-serializer`. Here an example for ``GET`` request to ``api/alarms/``::

        [
            {
                "id": 1,
                "monitor": [
                    {
                        "id": 1,
                        "lookups": "Q(slug__startswith='alarms') & Q(device__profile__name='Feeder')",
                        "start_time": "2018-04-02T15:42:16Z",
                        "duration": 0.0,
                        "frequency": "D",
                        "weight": 0,
                        "active": true,
                        "devices": [],
                        "variables": []
                    }
                ],
                "name": "Shield Incompatible",
                "slug": "shield-incompatible",
                "formula": "{{ var.value | bit:1 }}",
                "duration": 0.0,
                "description": "Cuando el equipo detecta que algun shield no es compatible con el software o hardware",
                "creator": null
            },
            {
                "id": 2,
                "monitor": [
                    {
                        "id": 1,
                        "lookups": "Q(slug__startswith='alarms') & Q(device__profile__name='Feeder')",
                        "start_time": "2018-04-02T15:42:16Z",
                        "duration": 0.0,
                        "frequency": "D",
                        "weight": 0,
                        "active": true,
                        "devices": [],
                        "variables": []
                    }
                ],
                "name": "Equipo Iniciado",
                "slug": "equipo-iniciado",
                "formula": "{{ var.value | bit:2 }}",
                "duration": 0.0,
                "description": "",
                "creator": null
            },

            .
            .
            .
        ]

   To get a single object in the API, we use ``pk`` to identify the object. We should put ``pk`` to ``api/alarms/<pk>/``.
   For example, if we want the object with ``pk=3``, then ``api/alarms/3/``, the output is::

       {
            "id": 3,
            "monitor": [
                {
                    "id": 1,
                    "lookups": "Q(slug__startswith='alarms') & Q(device__profile__name='Feeder')",
                    "start_time": "2018-04-02T15:42:16Z",
                    "duration": 0.0,
                    "frequency": "D",
                    "weight": 0,
                    "active": true,
                    "devices": [],
                    "variables": []
                }
            ],
            "name": "Sensor Temp. Desconectado",
            "slug": "sensor-temp-desconectado",
            "formula": "{{ var.value | bit:3 }}",
            "duration": 0.0,
            "description": "",
            "creator": null
       }

   For ``PUT`` method, you can modify any field. And can ``DElETE`` any alarm.