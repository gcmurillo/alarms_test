from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Alarm, AlarmEvent, Subscription, Notification, Monitor
from .serializers import AlarmSerializer, AlarmEventSerializer, SubscriptionSerializer, NotificationSerializer
from .signals import *
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.apps import apps
from guardian.shortcuts import assign_perm

Device = apps.get_model(settings.DEVICE_MODEL)
Var = apps.get_model(settings.VAR_MODEL)
Profile = apps.get_model(settings.PROFILE_MODEL)


client = Client()


class AlarmsAPITest(APITestCase):

    ''' Test for GET & POST Alarms API Methods '''

    def setUp(self):
        ''' Initializing test database '''

        User.objects.create_user(username='gcmurillo', password='abcd')
        url = reverse('alarms_list')
        data = {
            "name": "Alarma 1",
            "slug": "alarma1",
            "creator": 1,
            "formula": "..",
            "duration": 1,
            "description": "default",
            "monitor": []
        }
        self.client.post(url, data)

    def test_create_Alarm(self):
        ''' Create a new alarm object via POST method '''

        url = reverse('alarms_list')
        data = {
            "name": "Alarma 2",
            "slug": "alarma2",
            "creator": 1,
            "formula": "..",
            "duration": 1,
            "description": "default",
            "monitor": []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_failure_create_alarm(self):
        ''' Failure in create a new alarm, waiting for a 400 error code '''

        url = reverse('alarms_list')
        data = {
            "name": "Alarma 2",
            "slug": "alarma2",
            "creator": 3,
            "formula": "..",
            "duration": 1,
            "description": "default",
            "monitor": []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_alarms(self):
        ''' Get all Alarms objects in JSON format '''

        url = reverse('alarms_list')
        alarms = Alarm.objects.all()
        serializer = AlarmSerializer(alarms, many=True)
        response = self.client.get(url)
        self.assertEqual(serializer.data, response.data)

    def test_get_alarm(self):
        ''' Get alarm by pk '''

        alarm = Alarm.objects.get(pk=1)
        serializer = AlarmSerializer(alarm)
        response = self.client.get('/api/api_alarms/1/')
        self.assertEqual(serializer.data, response.data)

    def test_failure_get_alarm(self):
        ''' Failure getting an alarm by incorrect pk '''

        response = self.client.get('/api/api_alarms/100/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_should_update_alarm(self):
        ''' PUT information in a existing Alarm object '''

        data = {
            "name": "prueba PUT",
            "formula": "print('Esto es una prueba')"
        }
        response = self.client.put('/api/api_alarms/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_bad_request_alarm(self):
        ''' PUT incorrect information, generating a BAD REQUEST'''

        data =  {
            "name": "prueba PUT",
            "creator": "print('Esto es una prueba')"
        }
        response = self.client.put('/api/api_alarms/1/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_put_alarm(self):
        ''' Failure PUT in an not existing alarm '''

        data = {
            "name": "prueba PUT",
            "formula": "print('Esto es una prueba')"
        }
        response = self.client.put('/api/api_alarms/100/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_alarm(self):
        ''' Delete an Alarm '''
        response = self.client.delete('/api/api_alarms/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_failure_delete_alarm(self):
        ''' Delete a not existing alarm '''
        response = self.client.delete('/api/api_alarms/100/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EventsAPITest(APITestCase):

    ''' Test for GET & POST and others AlarmEvents Methods '''

    def setUp(self):
        ''' Initializing test database '''
        self.user = User.objects.create_user(username='user', is_active=True, is_staff=True)  # creating user
        self.user.set_password('abcd')
        self.user.save()
        self.user2 = User.objects.create_user(username='user_prueba', password='1234', is_active=True)
        self.alarm = Alarm.objects.create(name='alarma', slug='alarma', description='description')
        self.monitor = Monitor.objects.create(lookups='Q(slug__startswith="something")', active=True)
        assign_perm('can_subscribe', self.user, self.alarm)
        Subscription.objects.create(active=True, user=self.user, alarm=self.alarm, email=True)
        url = reverse('events_list')
        self.event = AlarmEvent.objects.create(alarm_type='US', created="2018-03-05T19:52:22Z", finished="2018-05-17T06:00:00Z",
                                  description='description', alarm=self.alarm)

    def test_get_single_event(self):
        ''' Success case of get single event '''

        self.client.login(username='user', password='abcd')
        event = AlarmEvent.objects.get(pk=1)
        serializer = AlarmEventSerializer(event)
        response = self.client.get('/api/api_alarms/events/1/')
        self.assertEqual(response.data, serializer.data)

    def test_finished_filter_no_selected(self):
        ''' Test finished filter for AlarmEvent no selected'''
        self.client.login(username='user', password='abcd')
        response = self.client.get('/api/api_alarms/events/?finished=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_finished_filter_true(self):
        ''' Test finished filter for AlarmEvent select True'''
        self.client.login(username='user', password='abcd')
        response = self.client.get('/api/api_alarms/events/?finished=3')
        self.assertEqual(len(response.data), 1)

    def test_finished_filter_false(self):
        ''' Test finished filter for AlarmEvent select False '''
        self.client.login(username='user', password='abcd')
        response = self.client.get('/api/api_alarms/events/?finished=2')
        self.assertEqual(len(response.data), 0)

    def test_finished_filter_bad_url(self):
        ''' Test finished filter for AlarmEvent select False '''
        self.client.login(username='user', password='abcd')
        response = self.client.get('/api/api_alarms/events/?finished=something')
        self.assertEqual(len(response.data), 1)

    def test_create_event(self):
        ''' Create a new Event via POST method '''

        url = reverse('events_list')
        data = {
            "alarm_type": "DV",
            "created": "2018-03-08T19:52:22Z",
            "finished": "2018-05-18T06:00:00Z",
            "description": "description",
            "content_type": []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_failure_create_event(self):
        ''' Failure creating a new event '''

        url = reverse('events_list')
        data = {
            "alarm_type": "RY",  # RY is not defined for alarm_type
            "created": "2018-03-08T19:52:22Z",
            "finished": "2018-05-18T06:00:00Z",
            "description": "description"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_events(self):
        ''' Get all events objects in JSON format '''

        url = reverse('events_list')
        events = AlarmEvent.objects.all()
        serializer = AlarmEventSerializer(events, many=True)
        self.client.login(username='user', password='abcd')
        response = self.client.get(url)
        self.assertEqual(response.data, serializer.data)

    def test_get_events_without_user(self):
        ''' Get events if youre subscribed '''
        self.client.login(username='user_prueba', password='1234')
        url = reverse('events_list')
        response = self.client.get(url)
        self.assertEqual(response.data, [])  # no user, no data

    def test_failure_get_event(self):
        ''' Failure getting a not existing event '''
        response = self.client.get('/api/api_alarms/events/100/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_get_event_no_permissions(self):
        ''' Failure get event, because user not logged or not subscribed to the alarm '''
        self.client.login(username='user_prueba', password='1234')
        response = self.client.get('/api/api_alarms/events/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_object_with_content_type_data(self):
        ''' Get object content type data, with correct serialization '''
        #todo: check
        self.client.login(username='user', password='abcd')
        self.event.content_type = [self.monitor, self.alarm]
        response = self.client.get('api/api_alarms/events/1/')

    def test_delete_event(self):
        ''' Delete an Event '''
        response = self.client.delete('/api/api_alarms/events/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_failure_delete_event(self):
        ''' Failing delete a not existng event '''
        response = self.client.delete('api/api_alarms/events/2020/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SubscriptionsAPITest(APITestCase):

    ''' Test for GET & POST and others Subscriptions Methods '''

    def setUp(self):
        ''' Initializing test database '''

        self.user = User.objects.create_superuser(username='gcmurillo', password='abcd', is_active=True, is_staff=True, email='correo@ejemplo.com') # creating user
        user2 = User.objects.create_user(username='user_prueba', password='1234', is_active=True) #creating user
        group = Group(name='grupo') #creating group
        group.save()
        self.user.groups.add(group)
        user2.groups.add(group)
        url = reverse('alarms_list')
        alarm_data = {
            "name": "Alarma 1",
            "slug": "alarma1",
            "creator": 1,
            "formula": "..",
            "duration": 1,
            "description": "default",
            "monitor": []
        }
        alarm_data2 = {
            "name": "Alarma 2",
            "slug": "alarma2",
            "creator": 1,
            "formula": "..",
            "duration": 8,
            "description": "default_alarma2",
            "monitor": []
        }
        self.client.post(url, alarm_data) # creating alarm1
        self.client.post(url, alarm_data2)# creating alarm2
        alarma = Alarm.objects.get(name='Alarma 1')
        assign_perm('can_subscribe', self.user, alarma)
        url = reverse('subscriptions_list')
        data = {
            'user': self.user.pk,
            'alarm': alarma.pk,
            'email': False
        }
        self.client.post(url, data) # create subscription 1

    def test_subscribed_to_the_same_alarm(self):
        ''' If a user is subscribed to an alarm, he can not subscribe to the same '''
        with self.assertRaises(ValidationError):

            url = reverse('subscriptions_list')
            data = {
                'user': 1,
                'alarm': 1,
                'email': False
            }
            response = self.client.post(url, data)
            self.assertNotEqual(status.HTTP_201_CREATED, response.status_code)

    def test_subscribed_to_another_alarm(self):
        ''' The successful case for subscription '''
        url = reverse('subscriptions_list')
        alarma = Alarm.objects.get(name='Alarma 2')
        assign_perm('can_subscribe', self.user, alarma)
        data = {
            'user': self.user.pk,
            'alarm': alarma.pk,
            'email': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_failure_subscribed_alarm_bad_request(self):
        ''' Failing a POST request with incorrect data '''
        url = reverse('subscriptions_list')
        data = {
            'user': 5,
            'alarm': 3,
            'email': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_subscriptions(self):
        ''' Get all Subscription objects '''

        url = reverse('subscriptions_list')
        subs = Subscription.objects.all()
        serializer = SubscriptionSerializer(subs, many=True)
        response = self.client.get(url)
        self.assertEqual(response.data, serializer.data)

    def test_get_subscription(self):
        ''' Get a Subscription '''

        sub = Subscription.objects.get(pk=1)
        serializer = SubscriptionSerializer(sub)
        response = self.client.get('/api/api_alarms/subscriptions/1/')
        self.assertEqual(response.data, serializer.data)

    def test_failure_get_subscription(self):
        ''' Failing get a not existing subscription '''
        response = self.client.get('/api/api_alarms/subscriptions/2020/')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_failure_put_should_update_subscription(self):
        ''' PUT information in a existing Subscription object, failing because only can change active status '''

        data = {
            "alarm": 1,
            "staff_template": "Alarma activada"
        }
        try:
            response = self.client.put('/api/api_alarms/subscriptions/1/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        except Exception as e:
            error = ValidationError(["User don't have permissions to subscribe to this alarm"])
            self.assertEqual(error.__str__(), e.__str__())

    def test_failure_put_changing_active_status_subscription(self):
        ''' Failure changing active status without permissions '''

        data = {
            "alarm": 1,
            "staff_template": "Alarma activada",
            "active": True
        }
        response = self.client.put('/api/api_alarms/subscriptions/1/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_changing_active_status_subscription(self):
        ''' Success changing active status with permissions '''

        self.client.login(username='gcmurillo', password='abcd')
        alarm = Alarm.objects.get(pk=1)
        assign_perm('can_subscribe', self.user, alarm)
        data = {
            "alarm": 1,
            "staff_template": "Alarma activada",
            "active": True
        }
        response = self.client.put('/api/api_alarms/subscriptions/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_changing_subscription(self):
        ''' Success changing active status with permissions '''

        self.client.login(username='gcmurillo', password='abcd')
        alarm = Alarm.objects.get(pk=1)
        assign_perm('can_subscribe', self.user, alarm)
        data = {
            "alarm": 1,
            "staff_template": "staff_template",
        }
        response = self.client.put('/api/api_alarms/subscriptions/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_bad_request_subscription(self):
        ''' Bad request PUT method '''
        self.client.login(username='gcmurillo', password='abcd')
        alarm = Alarm.objects.get(pk=1)
        assign_perm('can_subscribe', self.user, alarm)
        data = {
            "alarm": 1,
            "staff_template": "Alarma activada",
            "active": ":D",
        }
        response = self.client.put('/api/api_alarms/subscriptions/1/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_subscription_user_without_can_delete_perm(self):
        ''' Failing delete subscription for user without can delete permission '''

        response = self.client.delete('/api/api_alarms/subscriptions/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_no_existing_subscription(self):
        ''' Try delete no existing subscription '''
        response = self.client.delete('/api/api_alarms/subscriptions/1556/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_individual_subscription_for_group_subscription(self):
        ''' If a user is member of a group which subscribed to an alarm, and
            this user is subscribed to this alarm, the individual subscription is deleted '''
        url = reverse('subscriptions_list')
        data = {
            'group': 1,
            'alarm': 1,
            'email': False
        }
        group = Group.objects.get(id=1)
        alarm = Alarm.objects.get(id=1)
        assign_perm('can_subscribe', group, alarm)
        self.client.post(url, data) # create grupal subscription
        # Subscription 1 existed and user1 owned it. Where the group subscription is created, it is deleted
        response = self.client.get('api/api_alarms/subscriptions/1/')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class NotificationsAPITest(APITestCase):
    ''' Test fot GET & POST Notifications Methods '''

    def setUp(self):
        ''' Initializing test database '''

        self.user = User.objects.create_user(username='gcmurillo', password='abcd', email='gcmurillo@outlook.com')
        self.client.login(username='gcmurillo', password='abcd')
        User.objects.create_user(username='prueba', password='1234')
        url = reverse('events_list')
        event_data = {
            "alarm_type": "US",
            "created": "2018-03-05T19:52:22Z",
            "finished": "2018-05-17T06:00:00Z",
            "description": "description"
        }
        self.client.post(url, event_data)
        data = {
            'user': 2,
            'event': 1
        }
        url = reverse('notifications_list')
        self.client.post(url, data)

    def test_create_notification(self):
        ''' Create a new Notification via POST method '''

        data = {
            'user': 2,
            'event': 1
        }
        url = reverse('notifications_list')
        response = self.client.post(url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_failure_create_notification(self):
        ''' Failure create a new notification via POST method '''
        data = {
            'user': 22,
            'event': 53
        }
        url = reverse('notifications_list')
        response = self.client.post(url, data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_get_all_notifications_by_user(self):
        ''' Get all Notifications objects according user logged '''

        url = reverse('notifications_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notification(self):
        ''' Get a Notification '''

        notification = Notification.objects.get(pk=1)
        serializer = NotificationSerializer(notification)
        response = self.client.get('/api/api_alarms/notifications/1/')
        self.assertEqual(response.data, serializer.data)

    def test_failure_get_notification(self):
        ''' Failure get a notification with the incorrect user or not logged user '''

        self.client.logout()
        response = self.client.get('/api/api_alarms/notifications/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_should_update_notification_user_own_notification(self):
        ''' Success changing status of a notification '''

        data = {
            "status": "checked"
        }
        response = self.client.put('/api/api_alarms/notifications/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_should_not_update_notification_user_doesnt_own_notification(self):
        ''' Falling changing status of a notification with the incorrect user '''

        data = {
            "status": "checked"
        }
        self.client.login(username='prueba', password='1234')
        response = self.client.put('/api/api_alarms/notifications/1/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_should_not_update_notification_incorrect_information(self):
        ''' Failure, only status can be change '''
        data = {
            "user": 1
        }
        response = self.client.put('/api/api_alarms/notifications/1/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_bad_request(self):
        ''' Failure, only status can be change '''
        data = {
            "user": 'dasdr'
        }
        response = self.client.put('/api/api_alarms/notifications/1/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_put_information_not_existing_notification(self):
        ''' Only status can be change '''
        data = {
            "status": "checked"
        }
        response = self.client.put('/api/api_alarms/notifications/2020/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_notification(self):
        ''' Delete a Notification '''

        response = self.client.delete('/api/api_alarms/notifications/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_failure_delete_notification(self):
        ''' Failing delete a not existing notification '''

        response = self.client.delete('/api/api_alarms/notifications/2200/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_notification_n_email_in_event_creation(self):
        ''' Notification creation when an event is created '''

        device = Device.objects.create(serial='0001', name='device1')
        var = Var.objects.create(name='food', device=device)
        monitor = Monitor.objects.create(active=True, duration=1)
        monitor.devices.add(device)
        monitor.variables.add(var)
        url = reverse('alarms_list')
        data = {
            "name": "Alarma 1",
            "slug": "alarma1",
            "creator": 1,
            "formula": "..",
            "duration": 1,
            "description": "default",
            "monitor": 1
        }
        self.client.post(url, data)
        alarm = Alarm.objects.get(name='Alarma 1')
        assign_perm('can_subscribe', self.user, alarm)
        url = reverse('subscriptions_list')
        data = {
            'user': self.user,
            'alarm': 1,
            'email': True,
            'active': True
        }
        self.client.post(url, data)  # create subscription 1
        url = reverse('events_list')
        event_data = {
            "alarm_type": "DV",
            "finished": "2018-05-17T06:00:00Z",
            "description": "description",
            "device": 1,
            "variables": 1
        }
        self.client.post(url, event_data)
        self.assertEqual(1, Notification.objects.all().count())

    def test_get_no_existing_notification(self):
        response = self.client.get('/api/api_alarms/notifications/2200/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SubscriptionTest(TestCase):

    def setUp(self):
        ''' Initializing test database '''

        self.user = User.objects.create_superuser(username='gcmurillo', password='abcd', is_active=True, is_staff=True, email='correo@ejemplo.com') # creating user
        self.user2 = User.objects.create_user(username='user_prueba', password='1234', is_active=True) #creating user
        self.group = Group(name='grupo') #creating group
        self.group.save()
        self.user.groups.add(self.group)
        self.user2.groups.add(self.group)
        url = reverse('alarms_list')
        alarm_data = {
            "name": "Alarma 1",
            "slug": "alarma1",
            "creator": 1,
            "formula": "..",
            "duration": 1,
            "description": "default",
            "monitor": []
        }
        alarm_data2 = {
            "name": "Alarma 2",
            "slug": "alarma2",
            "creator": 1,
            "formula": "..",
            "duration": 8,
            "description": "default_alarma2",
            "monitor": []
        }
        self.client.post(url, alarm_data) # creating alarm1
        self.client.post(url, alarm_data2)# creating alarm2
        self.alarma = Alarm.objects.get(name='Alarma 1')
        assign_perm('can_subscribe', self.user, self.alarma)
        url = reverse('subscriptions_list')
        data = {
            'user': self.user.pk,
            'alarm': self.alarma.pk,
            'email': False
        }
        self.client.post(url, data) # create subscription 1

    def test_failure_subscribe_to_alarm_without_permissions(self):
        ''' Failing subscribe an alarm without permissions '''
        try:
            user = User.objects.create_user(username='nuevo')
            alarm = Alarm.objects.create(name='Alarma', formula='{{ var.value }} > 5')
            Subscription.objects.create(user=user, alarm=alarm, email=False)
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(["User don't have permissions to subscribe to this alarm"])
            self.assertEqual(error.__str__(), e.__str__())

    def test_subscribe_to_alarm_with_permissions(self):
        ''' Success subscribing to an alarm with permissions '''
        user = User.objects.create_user(username='user')
        alarm = Alarm.objects.create(name='alarma')
        n_subscriptions_before = Subscription.objects.all().count()
        assign_perm('can_subscribe', user, alarm)
        Subscription.objects.create(user=user, alarm=alarm)
        n_subscriptions_after = Subscription.objects.all().count()

        self.assertNotEquals(n_subscriptions_after, n_subscriptions_before)

    def test_delete_individual_subscription_with_permissions(self):
        ''' Delete subscription with a staff user '''
        self.client.login(username='gcmurillo', password='abcd')
        response = self.client.delete('/api/api_alarms/subscriptions/1/')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_failing_create_event_for_alarm_formula_by_device_update(self):
        ''' Failing create an event because incorrect formula '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.devices.add(device)
        alarma = Alarm.objects.create(name='alarma', formula='incorrect formula', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_notifications_before = Notification.objects.all()
        device.save()
        n_notifications_after = Notification.objects.all()

        self.assertEqual(len(n_notifications_before), len(n_notifications_after))

    def test_delete_individual_subscription(self):
        ''' Failing create an event because incorrect formula '''
        assign_perm('can_subscribe', self.group, self.alarma)
        user_before = Subscription.objects.all()[0].user
        Subscription.objects.create(group=self.group, alarm=self.alarma)
        user_after = Subscription.objects.all()[0].user
        self.assertNotEquals(user_before, user_after)

    def test_no_save_individual_subscription(self):
        ''' An User can subscribe to an Alarm twice '''
        try:
            Subscription.objects.create(user=self.user, alarm=self.alarma)
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['The user is subscribed to this alarm'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_user_subscribed_to_an_alarm_by_group(self):
        ''' An User can subscribe to an Alarm twice '''
        try:
            alarm = Alarm.objects.create(name='other_alarm')
            assign_perm('can_subscribe', self.group, alarm)
            Subscription.objects.create(group=self.group, alarm=alarm)
            assign_perm('can_subscribe', self.user, alarm)
            Subscription.objects.create(user=self.user, alarm=alarm)
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['The user is subscribed to the same alarm for a group'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_failing_create_event_for_var_validation_by_formula_field(self):
        ''' Failing create an event, because formula is incorrect '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var1 = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='device2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.variables.add(var1)
        alarma = Alarm.objects.create(name='alarma', formula='incorrect', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_notifications_before = Notification.objects.all()
        var1.save()
        n_notifications_after = Notification.objects.all()
        self.assertEqual(len(n_notifications_before), len(n_notifications_after))

    def test_create_a_monitor_lookup_field(self):
        ''' Creating a monitor adding a correct lookup '''
        lookup = "Q(slug__startswith='food'), (Q(device__id__in=[1,3]) | Q(device__name__startswith='Airador'))"
        Monitor.objects.create(lookups=lookup, duration=10, active=True)

        self.assertEqual(Monitor.objects.all().count(), 2)

    def test_failure_create_a_monitor_lookup_field(self):
        ''' Failing creating or editing a monitor in the lookup field '''
        lookup = "Q(slug__startswith='food'), (Q(device__id__in=[1,3]) | Q(device__name__startswitAirador')"
        Monitor.objects.create(lookups=lookup, duration=10, active=True)

        self.assertNotEqual(Monitor.objects.all().count(), 3)


class NotificationsTest(TestCase):

    def test_create_event_for_alarm_formula_by_device_update(self):
        ''' Create an event if formula field of alarm return True, for device post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.devices.add(device)
        alarma = Alarm.objects.create(name='alarma', formula='{{ vars.food.value }} < 5', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_notifications_before = Notification.objects.all()
        device.save()
        n_notifications_after = Notification.objects.all()

        self.assertNotEqual(n_notifications_before, n_notifications_after)

    def test_create_event_for_alarm_formula_by_device_update_multiple_devices_in_formula(self):
        ''' Create an event if formula field of alarm return True, for device post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        Var.objects.create(var_type='voltaje', name='voltaje', value=15, device=device, slug='voltaje')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.devices.add(device)
        alarma = Alarm.objects.create(name='alarma',
                                      formula='{{ vars.food.value }} < 5 and {{ vars.voltaje.value }} > 12',
                                      duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_notifications_before = Notification.objects.all()
        device.save()
        n_notifications_after = Notification.objects.all()

        self.assertNotEqual(n_notifications_before, n_notifications_after)

    def test_create_event_for_alarm_formula_by_device_update_condition_false(self):
        ''' Create an event if formula field of alarm return True, for device post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        Var.objects.create(var_type='food', name='food', value=20, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.devices.add(device)
        alarma = Alarm.objects.create(name='alarma', formula='{{ vars.food.value }} < 5', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_notifications_before = Notification.objects.all()
        device.save()
        n_notifications_after = Notification.objects.all()

        self.assertNotEqual(n_notifications_before, n_notifications_after)


    def test_failure_create_event_for_alarm_formula_looking_vars_for_monitor_lookups_field(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device_in=[1,3]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertEqual(n_events_after, n_events_before)

    def test_failure_create_event_for_alarm_formula_looking_vars_for_monitor_lookups_field_bad_formula(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,3]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value } == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertEqual(n_events_after, n_events_before)

    def test_failure_create_event_for_alarm_formula_looking_vars_for_monitor_lookups_alarm_duration_pass(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,3]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=-15)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_send_email_with_staff_template(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True, staff_template='template')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_send_email_with_user_template(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma,
                                    email=True, user_template='template', staff_template_text='')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_send_email_with_staff_template_text(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma,
                                    email=True, staff_template_text='<html> YEI </html>')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_send_email_with_user_template_text(self):
        ''' Failing create event, for a bad redacting lookup '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma,
                                    email=True, user_template_text='<html> YEI </html>', staff_template_text='')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)


    def test_create_event_for_alarm_formula_looking_vars_for_monitor_lookups_field(self):
        ''' Create events, if formula evaluation return true for vars got via lookups field evaluation '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__id__in=[1,3]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEqual(n_events_after, n_events_before)

    def test_create_event_for_alarm_formula_by_var_update_focus_var_type(self):
        ''' Create an event if formula field alarm return true, looking for all same var type '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var1 = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='device2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.variables.add(var1)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} < 5', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_notifications_before = Notification.objects.all()
        var1.save()
        n_notifications_after = Notification.objects.all()
        self.assertNotEqual(n_notifications_before, n_notifications_after)

    def test_create_event_for_alarm_formula_by_var_update(self):
        ''' Create an event if formula field alarm return true, for var post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True)
        monitor.devices.add(device)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} < 5', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = AlarmEvent.objects.all()
        var.save()
        n_events_after = AlarmEvent.objects.all()
        self.assertNotEqual(n_events_before, n_events_after)

    def test_create_event_monitor_var_selection(self):
        ''' Create an event if formula field alarm return true, for var post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True, lookups="")
        monitor.variables.add(var)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} < 5', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = AlarmEvent.objects.all()
        var.save()
        n_events_after = AlarmEvent.objects.all()
        self.assertNotEqual(n_events_before, n_events_after)

    def test_create_event_monitor_var_selection_with_preview_event(self):
        ''' Create an event if formula field alarm return true, for var post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True, lookups="")
        monitor.variables.add(var)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} < 5', duration=-15)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = AlarmEvent.objects.all()
        var.save()
        var.save()
        n_events_after = AlarmEvent.objects.all()
        self.assertNotEqual(n_events_before, n_events_after)

    def test_create_event_monitor_var_selection_with_bad_formula(self):
        ''' Create an event if formula field alarm return true, for var post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True, lookups="")
        monitor.variables.add(var)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value } < 5', duration=-15)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = AlarmEvent.objects.all()
        var.save()
        n_events_after = AlarmEvent.objects.all()
        self.assertNotEqual(n_events_before, n_events_after)

    def test_create_event_monitor_var_selection_with_condition_false(self):
        ''' Create an event if formula field alarm return true, for var post_save signal '''
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=20, device=device, slug='food')
        monitor = Monitor.objects.create(duration=10, active=True, lookups="")
        monitor.variables.add(var)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} < 5', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        assign_perm('can_subscribe', user, alarma)
        Subscription.objects.create(active=True, user=user, alarm=alarma, email=True)

        n_events_before = AlarmEvent.objects.all()
        var.save()
        n_events_after = AlarmEvent.objects.all()
        self.assertNotEqual(n_events_before, n_events_after)


    def test_mail_for_group_staff_template(self):
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        user2 = User.objects._create_user(username='user', password='1234', email='abc@gmail.com')
        group = Group.objects.create(name='group')
        group.user_set.add(user)
        group.user_set.add(user2)
        assign_perm('can_subscribe', group, alarma)
        Subscription.objects.create(active=True, group=group, alarm=alarma, email=True, staff_template='template')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_mail_for_group_staff_template_text(self):
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        user2 = User.objects._create_user(username='user', password='1234', email='abc@gmail.com')
        group = Group.objects.create(name='group')
        group.user_set.add(user)
        group.user_set.add(user2)
        assign_perm('can_subscribe', group, alarma)
        Subscription.objects.create(active=True, group=group, alarm=alarma, email=True, staff_template_text='<html> :D </html>')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_mail_for_group_user_template(self):
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        user2 = User.objects._create_user(username='user', password='1234', email='abc@gmail.com')
        group = Group.objects.create(name='group')
        group.user_set.add(user)
        group.user_set.add(user2)
        assign_perm('can_subscribe', group, alarma)
        Subscription.objects.create(active=True, group=group, alarm=alarma, email=True,
                                    staff_template_text='', user_template='template')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_mail_for_group_user_template_text(self):
        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        device1 = Device.objects.create(serial='0001', name='Airador1', connected=True, profile=profile)
        var = Var.objects.create(var_type='food', name='food', value=0, device=device1, slug='food')
        device2 = Device.objects.create(serial='0002', name='Airador2', connected=True)
        Var.objects.create(var_type='food', name='food', value=25, device=device2, slug='food')
        lookup = "Q(slug__startswith='food'), (Q(device__in=[1,2]) | Q(device__name__startswith='Airador'))"
        monitor = Monitor.objects.create(duration=10, active=True, lookups=lookup)
        alarma = Alarm.objects.create(name='alarma', formula='{{ var.value }} == 0', duration=1)
        alarma.monitor.add(monitor)
        user = User.objects.create_superuser(username='test_user', password='abcd', email='prueba@gmail.com')
        user2 = User.objects._create_user(username='user', password='1234', email='abc@gmail.com')
        group = Group.objects.create(name='group')
        group.user_set.add(user)
        group.user_set.add(user2)
        assign_perm('can_subscribe', group, alarma)
        Subscription.objects.create(active=True, group=group, alarm=alarma, email=True,
                                    staff_template_text='', user_template_text='<html> :D </html>')

        n_events_before = len(AlarmEvent.objects.all())
        var.save()
        n_events_after = len(AlarmEvent.objects.all())
        self.assertNotEquals(n_events_after, n_events_before)

    def test_clean_function_from_model_only_user_or_only_group(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, group=group, alarm=alarm).clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Only user or only group'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_user_or_group_are_required(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=None, group=None, alarm=alarm, user_template='template').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['BAD REQUEST. Check your selections.'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_without_template(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template_text='', staff_template_text='').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert staff or user template filename or write a staff or user template'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_with_user_n_staff_template(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template='template', staff_template='template',
                                        user_template_text='', staff_template_text='').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert only a template!'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_with_staff_template_n_staff_template_text(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template=None, staff_template='template',
                                        user_template_text='', staff_template_text='<html></html>').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert only a template!'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_with_staff_template_n_user_template_text(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template=None, staff_template='template',
                                        user_template_text='<html></html>', staff_template_text='').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert only a template!'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_with_user_template_n_staff_template_text(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template='template', staff_template=None,
                                        user_template_text='', staff_template_text='<html></html>').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert only a template!'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_with_user_template_n_user_template_text(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template='template', staff_template=None,
                                        user_template_text='<html></html>', staff_template_text='').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert only a template!'])
            self.assertEqual(error.__str__(), e.__str__())

    def test_clean_function_from_model_with_staff_template_text_n_user_template_text(self):

        try:
            user = User.objects.create_user(username='user', password='1234')
            group = Group.objects.create(name='group')
            group.user_set.add(user)
            alarm = Alarm.objects.create(name='alarm')
            assign_perm('can_subscribe', user, alarm)
            assign_perm('can_subscribe', group, alarm)
            Subscription.objects.create(user=user, alarm=alarm,
                                        user_template=None, staff_template=None,
                                        user_template_text='<html></html>', staff_template_text='<html></html>').clean()
        except Exception as e:
            # When a user doesn't have permissions to subscribe, an error raise
            error = ValidationError(['Insert only a template!'])
            self.assertEqual(error.__str__(), e.__str__())



class AlarmsTest(TestCase):

    def setUp(self):
        monitor = Monitor.objects.create(lookups="Q(slug__startswith='api_alarms') & Q(device__profile__name='Feeder')",
                                         duration=0, active=True)

        alarm = Alarm.objects.create(name='Shield Incompatible', formula='{{ var.value | bit:1 }}',
                                     description='Cuando el equipo detecta que algun shield no es compatible con el software o hardware')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Equipo Iniciado', formula='{{ var.value | bit:2 }}', description='')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor Temp. Desconectado', formula='{{ var.value | bit:3 }}',
                                     description='')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor 1 Desconectado', formula='{{ var.value | bit:4 }}',
                                     description='Cuando el equipo detecta que algun shield no es compatible con el software o hardware')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Firmware con Errores', formula='{{ var.value | bit:5 }}',
                                     description='Cuando el programa que llego para ser actualizado contiene errores')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Luz Desconectada', formula='{{ var.value | bit:6 }}',
                                     description='')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Alimentacion Deshabilitada', formula='{{ var.value | bit:7 }}',
                                     description='Cuando el equipo decide no alimentar, en otra variable se especifica un codigo indicando la causa')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Aspersor Desconectado', formula='{{ var.value | bit:8 }}',
                                     description='Sin consumo o muy bajo')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Aspersor Obstruido', formula='{{ var.value | bit:9 }}',
                                     description='Alto consumo')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Dosificador Desconectado', formula='{{ var.value | bit:10 }}',
                                     description='Sin consumo o muy bajo')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Tolva vacia', formula='{{ var.value | bit:11 }}',
                                     description='')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Dosificador Obstruido', formula='{{ var.value | bit:12 }}',
                                     description='Alto consumo')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor 2 Desconectado', formula='{{ var.value | bit:13 }}',
                                     description='Sin consumo o muy bajo')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Hidrófono Desconectado', formula='{{ var.value | bit:14 }}',
                                     description='Cunado no se detecta ruido')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Batería Baja', formula='{{ var.value | bit:15 }}',
                                     description='Cuando el voltaje de la batería es inferior a un valor prefijado')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Batería Alta', formula='{{ var.value | bit:16 }}',
                                     description='Cuando el voltaje de la batería es superior a un valor prefijado')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor 1 Bajo', formula='{{ var.value | bit:17 }}',
                                     description='Cuando el valor del sensor 1 es inferior a un valor prefijado')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor 1 Alto', formula='{{ var.value | bit:18 }}',
                                     description='Cuando el valor del sensor 1 es superior a un valor prefijado')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor 2 Bajo', formula='{{ var.value | bit:19 }}',
                                     description='Cuando el valor del sensor 2 es inferior a un valor prefijado')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Sensor 2 Alto', formula='{{ var.value | bit:20 }}',
                                     description='Cuando del valor del sensor 2 es superior a un valor prefijado')
        alarm.monitor.add(monitor)

        alarm = Alarm.objects.create(name='Alimentación Máxima', formula='{{ var.value | bit:31 }}',
                                     description='Cuando se supera alimentación máxima diaria definida por el usuario')
        alarm.monitor.add(monitor)

        profile = Profile.objects.create(profile_type='FE', name='Feeder', slug='feeder')
        self.device = Device.objects.create(serial='0001', name='device1', connected=True, profile=profile)
        alarm_var = Var.objects.create(var_type='api_alarms', name='api_alarms', value=0, device=self.device, slug='api_alarms')

    def test_shield_incompatible_alarm(self): # -> 2 bits
        ''' Shield incompatible alarm is activate and create a new AlarmEvent '''
        # 2 is 10 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 2
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Shield Incompatible')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_equipo_iniciado_alarm(self): # -> 3 bits
        ''' Equipo iniciado alarm is activate and create a new AlarmEvent '''
        # 4 is 100 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 4
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Equipo Iniciado')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_temp_desconectado_alarm(self):  # -> 4 bits
        ''' Sensor Temp desconectado alarm is activate and create a new AlarmEvent '''
        # 8 is 1000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 8
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor Temp. Desconectado')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_1_desconectado_alarm(self):  # -> 5 bits
        ''' Sensor 1 Desconectado alarm is activate and create a new AlarmEvent '''
        # 16 is 10000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 16
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor 1 Desconectado')

    def test_firmware_con_errores_alarm(self): # -> 6 bits
        ''' Firmware con Errores alarm is activate and create a new AlarmEvent '''
        # 32 is 100000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 32
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Firmware con Errores')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_luz_desconectada_alarm(self):  # -> 7 bits
        ''' Luz Desconectada alarm is activate and create a new AlarmEvent '''
        # 64 is 1000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 64
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Luz Desconectada')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_alimentacion_deshabilitada_alarm(self):  # -> 8 bits
        ''' Alimentacion deshabilitada alarm is activate and create a new AlarmEvent '''
        # 128 is 10000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 128
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Alimentacion Deshabilitada')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_aspersor_desconectado_alarm(self):  # -> 9 bits
        ''' Aspersor desconectado alarm is activate and create a new AlarmEvent '''
        # 256 is 100000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 256
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Aspersor Desconectado')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_aspersor_obstruido_alarm(self):  # -> 10 bits
        ''' Aspersor Obstruido alarm is activate and create a new AlarmEvent '''
        # 512 is 1000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 512
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Aspersor Obstruido')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_dosificador_desconectado_alarm(self):  # -> 11 bits
        ''' Dosificador Desconectado alarm is activate and create a new AlarmEvent '''
        # 1024 is 10000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 1024
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Dosificador Desconectado')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_tolva_vacia_alarm(self):  # -> 12 bits
        ''' Tolva vacia alarm is activate and create a new AlarmEvent '''
        # 2048 is 100000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 2048
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Tolva vacia')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_dosificador_obstruido_alarm(self):  # -> 13 bits
        ''' Dosificador Obstruido alarm is activate and create a new AlarmEvent '''
        # 4096 is 1000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 4096
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Dosificador Obstruido')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_2_desconectado_alarm(self):  # -> 14 bits
        ''' Sensor 2 Desconectado alarm is activate and create a new AlarmEvent '''
        # 8192 is 10000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 8192
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor 2 Desconectado')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_hidrofono_desconectado_alarm(self):  # -> 15 bits
        ''' Sensor 2 Desconectado alarm is activate and create a new AlarmEvent '''
        # 16384 is 100000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 16384
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Hidrófono Desconectado')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_bateria_baja_alarm(self):  # -> 16 bits
        ''' Bateria baja alarm is activate and create a new AlarmEvent '''
        # 32768 is 1000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 32768
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Batería Baja')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_bateria_alta_alarm(self):  # -> 17 bits
        ''' Bateria alta alarm is activate and create a new AlarmEvent '''
        # 65536 is 10000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 65536
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Batería Alta')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_1_bajo_alarm(self):  # -> 18 bits
        ''' Sensot 1 bajo alarm is activate and create a new AlarmEvent '''
        # 131072 is 100000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 131072
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor 1 Bajo')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_1_alto_alarm(self):  # -> 19 bits
        ''' Sensot 1 alto alarm is activate and create a new AlarmEvent '''
        # 262144 is 1000000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 262144
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor 1 Alto')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_2_bajo_alarm(self):  # -> 20 bits
        ''' Sensot 2 Bajo alarm is activate and create a new AlarmEvent '''
        # 524288 is 10000000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 524288
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor 2 Bajo')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_sensor_2_alto_alarm(self):  # -> 21 bits
        ''' Sensot 2 alto alarm is activate and create a new AlarmEvent '''
        # 1048576 is 100000000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 1048576
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Sensor 2 Alto')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_alimentacion_maxima_alarm(self):  # -> 32 bits
        ''' Alimentacion maxima alarm is activate and create a new AlarmEvent '''
        # 1048576 is 10000000000000000000000000000000 en binary, the alarm which looking for 1 bit is activate
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 2147483648
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event = AlarmEvent.objects.get(pk=1)

        self.assertEqual(event.alarm.name, 'Alimentación Máxima')
        self.assertNotEquals(n_events_after, n_events_before)

    def test_alarm_combination_1(self):
        ''' Test combination of api_alarms: Firmware con Errores (5) and Shield Incompatible (1) '''
        # 34 is 100010 in binary, the api_alarms selected are (5) and (1)
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 34
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event1 = AlarmEvent.objects.get(pk=1)
        event2 = AlarmEvent.objects.get(pk=2)

        self.assertEqual('Firmware con Errores', event2.alarm.name)
        self.assertEqual('Shield Incompatible', event1.alarm.name)
        self.assertNotEquals(n_events_after, n_events_before)

    def test_alarm_combination_2(self):
        ''' Test combination of api_alarms: Bateria Baja (15) and Hidrofono Desconectado (14) '''
        # 49152 is 1100000000000000 in binary, the api_alarms selected are (15) and (14)
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 49152
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event1 = AlarmEvent.objects.get(pk=1)
        event2 = AlarmEvent.objects.get(pk=2)

        self.assertEqual('Batería Baja', event2.alarm.name)
        self.assertEqual('Hidrófono Desconectado', event1.alarm.name)
        self.assertNotEquals(n_events_after, n_events_before)

    def test_alarm_combination_3(self):
        ''' Test combination of api_alarms: Equipo Iniciado (2), Alimentacion Deshabilitada (7),
            Asperson Obstruido (9) and Sensor 2 Alto (20) '''
        # 10492220 is 100000000001010000100 in binary, the api_alarms selected are (15) and (14)
        n_events_before = AlarmEvent.objects.all().count()
        alarm_var = Var.objects.get(pk=1)
        alarm_var.value = 1049220
        alarm_var.save()
        n_events_after = AlarmEvent.objects.all().count()
        event1 = AlarmEvent.objects.get(pk=1)
        event2 = AlarmEvent.objects.get(pk=2)
        event3 = AlarmEvent.objects.get(pk=3)
        event4 = AlarmEvent.objects.get(pk=4)

        self.assertEqual(event1.alarm.name, "Equipo Iniciado")
        self.assertEqual(event2.alarm.name, "Alimentacion Deshabilitada")
        self.assertEqual(event3.alarm.name, "Aspersor Obstruido")
        self.assertEqual(event4.alarm.name, "Sensor 2 Alto")
        self.assertNotEquals(n_events_after, n_events_before)

    def test_create_event_generic_alarm_1(self):
        '''
        Create an event, notification and send email if case, passing an object instance and alarm instance
        to create_event_for_not_specific_model, assuming that is call by a signal.
        The signal should call the function and pass the object instance and the alarm instance
        '''

        alarm = Alarm.objects.create(name='device_not_connected', slug='device_not_connected',
                                     formula='{{ var.connected }} == False')
        device = Device.objects.create(serial='01', name='device', connected=False)

        n_event_before = AlarmEvent.objects.all().count()
        create_event_for_not_specific_model_and_signal(sender_instance=device, alarm_instance=alarm)
        n_event_after = AlarmEvent.objects.all().count()

        self.assertNotEquals(n_event_after, n_event_before)

    def test_create_event_generic_alarm_2(self):
        '''
        Create an event, notification and send email if case, passing an object instance and alarm instance
        to create_event_for_not_specific_model, assuming that is call by a signal.
        The signal should call the function and pass the object instance and the alarm instance
        '''

        alarm = Alarm.objects.create(name='device_not_connected', slug='device_not_connected',
                                     formula='{{ var.active }} == True')
        monitor = Monitor.objects.create(lookups="Q(slug__startswith='some')", active=True, duration=0)

        n_event_before = AlarmEvent.objects.all().count()
        create_event_for_not_specific_model_and_signal(sender_instance=monitor, alarm_instance=alarm)
        n_event_after = AlarmEvent.objects.all().count()

        self.assertNotEquals(n_event_after, n_event_before)

    def test_create_event_generic_alarm_formula_error(self):
        '''
        Create an event, notification and send email if case, passing an object instance and alarm instance
        to create_event_for_not_specific_model, assuming that is call by a signal.
        The signal should call the function and pass the object instance and the alarm instance
        '''

        alarm = Alarm.objects.create(name='device_not_connected', slug='device_not_connected',
                                     formula='{{ var.active } == True')
        monitor = Monitor.objects.create(lookups="Q(slug__startswith='some')", active=True, duration=0)

        n_event_before = AlarmEvent.objects.all().count()
        create_event_for_not_specific_model_and_signal(sender_instance=monitor, alarm_instance=alarm)
        n_event_after = AlarmEvent.objects.all().count()

        self.assertEqual(n_event_after, n_event_before)

    def test_create_event_generic_alarm_condition_false(self):
        '''
        Create an event, notification and send email if case, passing an object instance and alarm instance
        to create_event_for_not_specific_model, assuming that is call by a signal.
        The signal should call the function and pass the object instance and the alarm instance
        '''
        self.device.connected = False
        alarm = Alarm.objects.create(name='device_not_connected', slug='device_not_connected',
                                     formula='{{ var.active }} == True')
        monitor = Monitor.objects.create(lookups="Q(device__name='device1')", active=True, duration=0)

        n_event_before = AlarmEvent.objects.all().count()
        create_event_for_not_specific_model_and_signal(sender_instance=monitor, alarm_instance=alarm)
        n_event_after = AlarmEvent.objects.all().count()

        self.assertNotEquals(n_event_after, n_event_before)

