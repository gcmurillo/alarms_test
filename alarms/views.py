from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import Q
from django_filters import rest_framework as filters
from django.http import Http404
from .models import Monitor, Alarm, AlarmEvent, Subscription, Notification
from .serializers import MonitorSerializer, AlarmSerializer, AlarmEventSerializer, SubscriptionSerializer, \
                         NotificationSerializer
from guardian.shortcuts import get_user_perms, get_group_perms
from .filters import SubscriptionFilter, NotificationFilter, AlarmEventFilter

from django.apps import apps
Device = apps.get_model(settings.DEVICE_MODEL)
Var = apps.get_model(settings.VAR_MODEL)
VarLog = apps.get_model(settings.VARLOG_MODEL)


class AlarmList(APIView):

    """
    List all Alarm, or create a new Alarm
    """

    def get(self, request, format=None):

        """
        Get all alarms
        """
        alarms = Alarm.objects.all()
        serializer = AlarmSerializer(alarms, many=True)
        return Response(serializer.data)

    def post(self, request):

        """
        Post an alarm via POST Method
        """
        serializer = AlarmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlarmDetail(APIView):

    """
    GET, PUT AND DELETE METHODS FOR Monitor
    """

    def get_object(self, pk):
        try:
            return Alarm.objects.get(pk=pk)
        except Alarm.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):

        """
        Get a Alarm by PK
        """
        try:
            alarm = Alarm.objects.get(pk=pk)
            serializer = AlarmSerializer(alarm)
            return Response(serializer.data)
        except Alarm.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):

        """
        Put information in a existing alarm by pk'''
        """
        try:
            alarm = Alarm.objects.get(pk=pk)
            serializer = AlarmSerializer(alarm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Alarm.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):

        """
        Delete an existing alarm by pk
        """
        alarm = self.get_object(pk=pk)
        alarm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlarmEventList(generics.ListAPIView):

    """
    List AlarmEvents by filters, or create a new AlarmEvent
    """
    serializer_class = AlarmEventSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_class = AlarmEventFilter

    def get_queryset(self):

        """
        Getting events which the user is subscribed
        """
        alarms = Subscription.objects.filter(Q(user__in=[self.request.user])
                                         | Q(group__in=self.request.user.groups.all())).values_list('alarm', flat=True)
        return AlarmEvent.objects.filter(alarm__in=alarms)

    def post(self, request, format=None):

        """
        Create new event
        """
        serializer = AlarmEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlarmEventDetail(APIView):

    """
    GET, PUT AND DELETE METHODS FOR AlarmEvent
    """

    def get(self, request, pk, format=None):

        """
        Get event information by pk, if the user is subscribed to this
        """
        try:
            event = AlarmEvent.objects.get(pk=pk)
            serializer = AlarmEventSerializer(event)
            my_events = AlarmEventList.get_queryset(self)
            if event in my_events:
                return Response(serializer.data)
            return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "Not Authorized User"})
        except AlarmEvent.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)  # if notification does not exist

    def delete(self, request, pk, format=None):

        """
        Delete event object
        """
        event = AlarmEvent.objects.get(pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionList(generics.ListAPIView):

    """
    List Subscriptions by filters, or create a new Subscription
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = ('user', 'group')
    filter_backends = (filters.DjangoFilterBackend, )
    filter_class = SubscriptionFilter

    def post(self, request, format=None):
        ''' Create new subscription '''
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionDetail(APIView):

    """
    GET, PUT AND DELETE METHODS FOR Subscriptions
    """

    def get(self, request, pk, format=None):

        """
        Get an element by pk
        """
        try:
            sub = Subscription.objects.get(pk=pk)
            serializer = SubscriptionSerializer(sub)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):

        """
        Only can change the active status
        """
        sub = Subscription.objects.get(pk=pk)
        sub_serializer = SubscriptionSerializer(sub)
        request_serializer = SubscriptionSerializer(sub, data=request.data)
        if request_serializer.is_valid():
            user_id = sub_serializer.data['user']
            if 'active' in self.request.data.keys():  # If want to change active status
                # True if user is user owner or have permissions
                if self.request.user.id == user_id or self.request.user.has_perm('can_change_activation', Subscription):
                    request_serializer.save()
                    return Response(request_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(data={"detail": "Not Authorized User"}, status=status.HTTP_403_FORBIDDEN)
            else:
                request_serializer.save()
                return Response(request_serializer.data, status=status.HTTP_200_OK)
        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):

        """
        Delete subscription if user is owner or have permissions
        """
        try:
            sub = Subscription.objects.get(pk=pk)
            serializer = SubscriptionSerializer(sub)
            user_id = serializer.data['user']
            # If is staff and don't have delete permission, can't delete the subscription.
            if self.request.user.id == user_id or "can_delete_alarm" in get_user_perms(self.request.user, sub):
                sub.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(data={"detail": "Not Authorizated User"}, status=status.HTTP_403_FORBIDDEN)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class NotificationList(generics.ListAPIView):

    """
    List Notifications by Filters
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_class = NotificationFilter

    def get_queryset(self):

        """
        Get user's notifications only
        """
        return Notification.objects.filter(user=self.request.user)

    def post(self, request, format=None):

        """
        Create a new notification
        """
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationDetail(APIView):

    """
    GET, PUT AND DELETE METHODS for Notifications '''
    """

    def get(self, request, pk, format=None):

        """
        Get notification by pk, if user is owner
        """
        try:
            notification = Notification.objects.get(pk=pk)
            serializer = NotificationSerializer(notification)
            if serializer.data['user'] == request.user.id:
                return Response(serializer.data)
            return Response(data={'detail': 'Not Authorized User'}, status=status.HTTP_403_FORBIDDEN)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):

        """
        Only can change status information
        """
        try:
            notification = Notification.objects.get(pk=pk)
            noti_serializer = NotificationSerializer(notification)
            request_serializer = NotificationSerializer(notification, data=request.data)
            if request_serializer.is_valid():
                user_id = noti_serializer.data['user']
                if 'status' in self.request.data.keys() and len(self.request.data.keys()) == 1:  # Only can change status field
                    if user_id == self.request.user.id:
                        request_serializer.save()
                        return Response(request_serializer.data, status=status.HTTP_200_OK)  # if ok
                    return Response(data={"detail": "Not Authorized User"}, status=status.HTTP_403_FORBIDDEN)  # if not correct user
                return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # if not correct json (only status information)
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  #  if data is not correct
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):

        """
        Delete a notification by pk '''
        """
        try:
            notification = Notification.objects.get(pk=pk)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


