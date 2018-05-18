
from django.conf.urls import url
from .views import AlarmEventList, AlarmEventDetail, SubscriptionList, SubscriptionDetail, AlarmList, AlarmDetail, NotificationList, NotificationDetail
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.generic import TemplateView

urlpatterns = [
    ### API endpoints ###
    url(r'api/alarms/$', AlarmList.as_view(), name='alarms_list'),
    url(r'api/alarms/(?P<pk>[0-9]+)/$', AlarmDetail.as_view(), name='alarms_detail'),
    url(r'api/alarms/events/$', AlarmEventList.as_view(), name='events_list'),
    url(r'api/alarms/events/(?P<pk>[0-9]+)', AlarmEventDetail.as_view(), name='events_detail'),
    url(r'api/alarms/subscriptions/$', SubscriptionList.as_view(), name='subscriptions_list'),
    url(r'api/alarms/subscriptions/(?P<pk>[0-9]+)/$', SubscriptionDetail.as_view(), name='subscriptions_detail'),
    url(r'api/alarms/notifications/$', NotificationList.as_view(), name='notifications_list'),
    url(r'api/alarms/notifications/(?P<pk>[0-9]+)/$', NotificationDetail.as_view(), name='notifications_detail'),
    ### END API endpoints ###

]

urlpatterns = format_suffix_patterns(urlpatterns)