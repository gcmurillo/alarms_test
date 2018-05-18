from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from .models import Monitor, Alarm, AlarmEvent, Subscription, Notification
from django.apps import apps
from django.contrib.auth.models import User, Group
from .forms import SubscriptionModelForm, MonitorModelForm
from guardian.admin import GuardedModelAdmin
Device = apps.get_model(settings.DEVICE_MODEL)
Var = apps.get_model(settings.VAR_MODEL)

# filtros para Monitor


class DeviceListFilter_Monitor(admin.SimpleListFilter):

    ''' Filtrado de los Monitors en Admin Site por devices '''
    title = 'Devices'
    parameter_name = 'devices'
    default_value = None

    def lookups(self, request, model_admin):

        devices_list = []
        queryset = Device.objects.all()
        for dev in queryset:
            devices_list.append(
                (str(dev.pk), dev.name)
            )
        return devices_list

    def queryset(self, request, queryset):

        if self.value():
            return queryset.filter(devices=self.value())


class VarsListFilter_Monitor(admin.SimpleListFilter):

    ''' Filtrado de Monitors en Admin Site por vars'''

    title = 'Variable'
    parameter_name = 'variables'
    default_value = None

    def lookups(self, request, model_admin):

        vars_list = []
        queryset = Var.objects.all()
        for var in  queryset:
            vars_list.append(
                (str(var.pk), var.slug)
            )

        return vars_list

    def queryset(self, request, queryset):

        if self.value():
            return queryset.filter(variables=self.value())

#fin filtros para Monitor


def set_active_monitor_true(modeladmin, request, queryset):
    queryset.update(active=True)
set_active_monitor_true.short_description = 'Set active status True'


def set_active_monitor_false(modeladmin, request, queryset):
    queryset.update(active=False)
set_active_monitor_false.short_description = 'Set active status False'


def set_start_time_monitor_today(modeladmin, requets, queryset):
    queryset.update(start_time=timezone.now())


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'weight', 'duration', 'frequency', 'lookups', 'start_time', 'active')
    list_filter = (DeviceListFilter_Monitor, 'active', 'start_time')
    form = MonitorModelForm
    ordering = ('start_time', )
    search_fields = ('pk', )  # revisar
    fieldsets = ((None,
                  {
                    'fields': (('devices', 'variables', 'lookups'), 'start_time',
                               'duration', 'frequency', 'weight', 'active')
                  }),
                 )
    actions = [set_active_monitor_false, set_active_monitor_true, set_start_time_monitor_today]
# filtros para Alarm


class CreatorListFilter_Alarm(admin.SimpleListFilter):

    ''' Filtrado de Alarm en Admin Site por Creator '''
    title = 'Creator'
    parameter_name = 'creator'
    default_value = None

    def lookups(self, request, model_admin):

        creators_list = []
        queryset = User.objects.all()
        for creator in queryset:
            creators_list.append(
                (str(creator.pk), creator.username)
            )

        return creators_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(creator=self.value())

#fin de filtros para Alarm


@admin.register(Alarm)
class AlarmAdmin(GuardedModelAdmin):
    list_display = ('name', 'slug', 'creator', 'get_monitors', 'duration', 'description', 'formula')
    list_filter = (CreatorListFilter_Alarm,)
    search_fields = ('name', 'creator__username', 'slug')
    autocomplete_fields = ('creator', )
    prepopulated_fields = {'slug': ('name', )}
    fieldsets = ((None,
                 {
                     'fields': (('name', 'slug'), 'creator', 'formula', 'duration', 'description', 'monitor')
                 }),
                 )

# Filtros para AlarmEvent

class AlarmTypeListFilter_AlarmEvent(admin.SimpleListFilter):

    ''' Filtrado para Alarm Event por alarm_type '''
    title = 'Tipo'
    parameter_name = 'alarm_type'
    default_value = None

    def lookups(self, request, model_admin):
        USER = 'US'
        DEVICE = 'DV'
        NO_DEVICE = 'ND'

        ALARM_CHOICES = (
            (USER, 'User'),
            (DEVICE, 'Device'),
            (NO_DEVICE, 'No-Device')
        )

        return ALARM_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(alarm_type=self.value())


class DeviceListFilter_AlarmEvent(admin.SimpleListFilter):

    ''' Filtrado de los Monitors en Admin Site por devices '''
    title = 'Device'
    parameter_name = 'device'
    default_value = None

    def lookups(self, request, model_admin):

        devices_list = []
        queryset = Device.objects.all()
        for dev in queryset:
            devices_list.append(
                (str(dev.pk), dev.name)
            )
        return devices_list

    def queryset(self, request, queryset):

        if self.value():
            return queryset.filter(device=self.value())


# Fin filtros para AlarmEvent


@admin.register(AlarmEvent)
class AlarmEventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'alarm', 'alarm_type', 'created', 'finished', 'device', 'variables', 'get_contents_type', 'description')
    list_filter = (AlarmTypeListFilter_AlarmEvent, DeviceListFilter_AlarmEvent, VarsListFilter_Monitor, 'created', 'alarm')
    #search_fields = ('__str__', 'alarm_type',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

# filtros para Subscriptions

class UserListFilter_Subscription(admin.SimpleListFilter):

    ''' Filtrado de Subscription por User '''
    title = 'User'
    parameter_name = 'user'
    default_value = None

    def lookups(self, request, model_admin):

        users_list = []
        queryset = User.objects.all()
        for user in queryset:
            users_list.append(
                (str(user.pk), user.username)
            )

        return users_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user=self.value())


class GroupListFilter_Subscription(admin.SimpleListFilter):

    ''' Filtradpo de Subscription por Group '''
    title = 'Group'
    parameter_name = 'group'
    default_value = None

    def lookups(self, request, model_admin):

        groups_list = []
        queryset = Group.objects.all()
        for group in queryset:
            groups_list.append(
                (str(group.pk), group.name)
            )

        return groups_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group=self.value())


class AlarmListFilter_Subscription(admin.SimpleListFilter):

    ''' Filtrado de Subscription por Alarm '''
    title = 'Alarm'
    parameter_name = 'alarm'
    default_value = None

    def lookups(self, request, model_admin):

        alarms_list = []
        queryset = Alarm.objects.all()
        for alarm in queryset:
            alarms_list.append(
                (str(alarm.pk), alarm.slug)
            )

        return alarms_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(alarm=self.value())

# fin filtros para Subscription


def check_email_false(modeladmin, request, queryset):
    queryset.update(email=False)
check_email_false.short_description = 'Check email false'


def check_email_true(modeladmin, request, queryset):
    queryset.update(email=True)
check_email_true.short_description = 'Check email true'


def set_active_true(modeladmin, request, queryset):
    queryset.update(active=True)
set_active_true.short_description = 'Set active status true'


def set_active_false(modeladmin, request, queryset):
    queryset.update(active=False)
set_active_false.short_description = 'Set active status false'


@admin.register(Subscription)
class SubscriptionAdmin(GuardedModelAdmin):
    list_display = ('__str__', 'user', 'group', 'alarm', 'email', 'staff_template', 'user_template',
                    'active')
    list_filter = (UserListFilter_Subscription, GroupListFilter_Subscription, AlarmListFilter_Subscription, 'email')
    fieldsets = ((None, {
                     'fields': ('active', 'created', 'alarm', 'email',)
                 }),
                 ('User or group', {
                     'fields': ('user', 'group')
                 }),
                 ('Email Templates', {
                     'fields': ('staff_template', 'user_template', 'staff_template_text', 'user_template_text')
                 }),

                 )
    actions = [check_email_false, check_email_true, set_active_false, set_active_true]

    form = SubscriptionModelForm

# filtros para Notification


class EventTypeListFilter_Notification(admin.SimpleListFilter):

    ''' Filtado de Notification por Tipo de Evento '''
    title = 'Alarm Type'
    parameter_name = 'event'
    default_value = None

    def lookups(self, request, model_admin):

        USER = 'US'
        DEVICE = 'DV'
        NO_DEVICE = 'ND'

        ALARM_CHOICES = (
            (USER, 'User'),
            (DEVICE, 'Device'),
            (NO_DEVICE, 'No-Device')
        )

        return ALARM_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(event__alarm_type=self.value())


class UserListFilter_Notification(admin.SimpleListFilter):

    ''' Filtrado de Notificacion por User '''

    title = 'User'
    parameter_name = 'user'
    default_value = None

    def lookups(self, request, model_admin):
        user_list = []
        queryset = User.objects.all()
        for user in queryset:
            user_list.append(
                (str(user.pk), user.username)
            )
        return user_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user=self.value())


def set_status_checked(modeladmin, request, queryset):
    queryset.update(status='checked')
set_status_checked.short_description = 'Set status checked'


def set_status_unchecked(modeladmin, request, queryset):
    queryset.update(status='unchecked')
set_status_unchecked.short_description = 'Set status unchecked'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'event', 'status', 'created')
    list_filter = (EventTypeListFilter_Notification, UserListFilter_Notification, 'status', 'created')
    ordering = ('-pk', )
    actions = [set_status_checked, set_status_unchecked]