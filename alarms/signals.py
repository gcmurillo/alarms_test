from django.conf import settings
from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.template import Template, Context
from django.template.loader import get_template
from .models import Monitor, Alarm, AlarmEvent, Subscription, Notification
from .serializers import SubscriptionSerializer
from guardian.shortcuts import get_user_perms, get_group_perms
from django.utils import timezone
from django.db.models import Q  # don't delete me

from django.apps import apps
Device = apps.get_model(settings.DEVICE_MODEL)
Var = apps.get_model(settings.VAR_MODEL)
VarLog = apps.get_model(settings.VARLOG_MODEL)


@receiver(post_save, sender=AlarmEvent)
def notifications_n_email_after_event_creation(sender, instance, **kwargs):

    """
    Create a Notification and send email (if case), when a event is created
    :param sender: AlarmEvent
    """
    alarm = instance.alarm  # Alarm which generated the event

    subscriptions = Subscription.objects.filter(alarm=alarm)  # Getting the subscriptions associated with alarms
    sub_serializer = SubscriptionSerializer(subscriptions, many=True)
    send = []   # list of emails which the mail was send
    notificated = []  # list with users notificated

    # If no device, no variable and no content_type, there is nothing to send yet. Cancel notification and email
    if instance.device is None and instance.variables is None and len(instance.content_type.all()) == 0 :
        return
    for sub in sub_serializer.data:  # Itering for subscription
        if sub['user'] is not None:  # if user field isn't NULL AND not Group
            user = User.objects.get(id=sub['user'])
            if sub['active'] and user not in notificated: # if subscription is active
                Notification.objects.create(user=user, event=instance)  # creating notification
                notificated.append(user)    # adding user to the notified list
                if sub['email']:  # if email option is checked
                    email = user.email
                    if email not in send:  # for dont repeat email
                        # Get a dict with relevant information about the event
                        context = {'event': instance,
                                   'alarm': instance.alarm,
                                   'user': user,
                                   'device': instance.device,
                                   'var': instance.variables,
                                   'content_type': instance.content_type.all()}
                        plain_text = get_template('mail.txt')  # Plain text template
                        text_content = plain_text.render(context)
                        subject = 'Event Alert: ' + instance.__str__()
                        from_email = 'noreply@localhost.com'
                        to = email
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        try:
                            if sub['staff_template'] is not None:
                                htmly = get_template(sub['staff_template'])  # Define the HTML template
                                html_content = htmly.render(context)  # Rendering the templates with context information
                            elif sub['staff_template_text'] != "":
                                htmly = Template(sub['staff_template_text'])
                                html_content = htmly.render(Context(context))
                            elif sub['user_template'] is not None:
                                htmly = get_template(sub['user_template'])  # Define the HTML template
                                html_content = htmly.render(context)  # Rendering the templates with context information
                            elif sub['user_template_text'] != "":
                                htmly = Template(sub['user_template_text'])
                                html_content = htmly.render(Context(context))
                            msg.attach_alternative(html_content, 'text/html')
                            msg.send()
                        except:
                            msg.send()
                        print('Mail send to %s' % email)

        if sub['group'] is not None:  # if is group and not user
            users_mail_list = []  # list with staff users instances
            if sub['active']:  # if subscription is active
                group = Group.objects.get(pk=sub['group'])  # Getting the group by id
                users = User.objects.filter(groups__name=group)  # getting the users for group
                context = {'event': instance,
                           'alarm': instance.alarm,
                           'user': group,
                           'device': instance.device,
                           'var': instance.variables}
                for user in users:  # Iterating users
                    if user not in notificated:
                        Notification.objects.create(user=user, event=instance) # creating notification
                        notificated.append(user) # adding user to notificated list
                    if sub['email']:
                        mail = user.email  # Adding the email for users in the user list
                        if mail not in send:  # for don't repeat email
                            users_mail_list.append(mail)
                            send.append(mail)
                # After getting all the emails and classifying it for staff and not staff members
                plain_text = get_template('mail.txt')  # Plain text template
                text_content = plain_text.render(context)
                subject = 'Event Alert: ' + instance.__str__()
                from_email = 'noreply@localhost.com'
                msg = EmailMultiAlternatives(subject, text_content, from_email, users_mail_list)
                try:
                    if sub['staff_template'] is not None:
                        htmly = get_template(sub['staff_template'])  # Define the HTML template
                        html_content = htmly.render(context)  # Rendering the templates with context information
                    elif sub['staff_template_text'] != "":
                        htmly = Template(sub['staff_template_text'])
                        html_content = htmly.render(Context(context))
                    elif sub['user_template'] is not None:
                        htmly = get_template(sub['user_template'])  # Define the HTML template
                        html_content = htmly.render(context)  # Rendering the templates with context information
                    elif sub['user_template_text'] != "":
                        htmly = Template(sub['user_template_text'])
                        html_content = htmly.render(Context(context))
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send()
                except:
                    msg.send()
                print('Mail send to %s' % str(users_mail_list))


@receiver(pre_save, sender=Subscription)
def delete_individual_subscriptions_for_grupal_subscription(sender, instance, **kwargs):

    """
    Delete individual subscriptions for group subscriptions,
    if a new subscription is creating or any is modified, the users in the group
    with individual subscriptions to the same alarm, this subscription is delete
    :param sender: Subscription
    """
    if instance.group is not None:  # Only for group subscription creation
        users = User.objects.filter(groups__name=instance.group)
        subs = Subscription.objects.filter(user__in=users)
        for sub in subs:
            if sub.alarm == instance.alarm:
                print('%s deleted' % sub)
                sub.delete()


@receiver(pre_save, sender=Subscription)
def no_save_individual_subscription(sender, instance, **kwargs):

    """
    Stop saving individual subscription if the user is member of a group subscribed to the same alarm
    :param sender: Subscription
    """
    try:
        Subscription.objects.get(pk=instance.pk) # looking if the subscription exist, if the case, we assume here is updating active status or email status
    except:
        if instance.user is not None:
            subs_ids = instance.user.groups.values_list('subscription')
            for sub in subs_ids:
                if None not in sub:
                    alarm = Subscription.objects.get(id=sub[0]).alarm
                    if alarm == instance.alarm:
                        raise ValidationError('The user is subscribed to the same alarm for a group')

            subs = Subscription.objects.filter(user=instance.user)
            for sub in subs:
                if sub.alarm == instance.alarm:
                    raise ValidationError('The user is subscribed to this alarm')


@receiver(pre_save, sender=Subscription)
def no_save_subscription_if_dont_have_permissions(sender, instance, **kwargs):

    """
    Stop saving individual or group subscription if user or group don't have
    permissions to subscribe to the alarm
    :param sender: Subscription
    """
    user = instance.user if instance.user else None
    group = instance.group if instance.group else None

    if user:
        if 'can_subscribe' not in get_user_perms(user, instance.alarm):
            raise ValidationError("User don't have permissions to subscribe to this alarm")
    elif group:
        if 'can_subscribe' not in get_group_perms(group, instance.alarm):
            raise ValidationError("Group don't have permissions to subscribe to this alarm")
    else:
        raise ValidationError("BAD REQUEST. Check your selections.")


@receiver(post_save, sender=Device)
def create_event_for_alarm_formula_by_device_update(sender, instance, **kwargs):

    """
    Create event by formula field in alarm referenced by updated device
    :param sender: Device
    """
    alarms = Alarm.objects.filter(monitor__devices=instance, monitor__active=True) # Get the alarms reference by monitors list
    #vars = instance.vars.values('value', 'slug', 'var_type')
    vars = Var.objects.filter(device=instance).values('value', 'slug', 'var_type')
    context = {
        'vars': {var_item['var_type']: var_item for var_item in vars},
        'device': instance
    }
    var_types = [var_item['var_type'] for var_item in vars]  # Device var_types
    for alarm in alarms:
        condition = False
        try:
            template = Template(alarm.formula)  # example -> {{ vars.voltaje.value }} > 12
            condition = eval(template.render(Context(context)))  # eval the formula with values in context dictionary
        except:
            print('Error al ejecutar formula de alarma ' + alarm.name)
            condition = None
            break  # if formula false, next alarm or variable

        n_vars_in_formula = 0  # count the vars in formula field
        var_in_formula = None
        if condition:  # if formula expression return True
            for var_type in var_types:
                if var_type in alarm.formula:
                    n_vars_in_formula += 1
                    var_in_formula = Var.objects.get(var_type=var_type, device=instance)
            # Only work for one var in formula, if two or more, is hard to determinate which generate alarm
            # in case two or more variables are in formula, 'variables' field get null value.
            if n_vars_in_formula == 1:
                AlarmEvent.objects.create(alarm=alarm, device=instance, variables=var_in_formula, description=alarm.description)
            else:
                AlarmEvent.objects.create(alarm=alarm, device=instance, description=alarm.description)
            print('Evento creado')
        elif condition == False:  # if formula return False, NO CASE IF FORMULA FAULTS
            for var_type in var_types:
                if var_type in alarm.formula:
                    n_vars_in_formula += 1
                    var_in_formula = Var.objects.get(var_type=var_type, device=instance)
            # only works for only one var, too.
            # In this, we want to set finished date to the events with same var and device, don't have finished date,
            # and because false, have a good value for variable.
            if n_vars_in_formula == 1:
                AlarmEvent.objects.filter(alarm=alarm, device=instance, variables=var_in_formula,
                                          finished=None).update(finished=timezone.now(), description=alarm.description)


@receiver(post_save, sender=Var)
def create_event_for_alarm_formula_looking_vars_for_monitor_lookups_field(sender, instance, **kwargs):

    """
    Create event by alarm formula field for alarm type, no only variable instance
    :param sender: Var
    """
    monitors = []
    vars = []
    for monitor in Monitor.objects.all():
        if monitor.lookups:
            try:
                vars_query = eval('Var.objects.filter(%s)' % monitor.lookups)
            except Exception as e:
                vars_query = []
                print("Error executing lookup %s in monitor %s. Details: %s" % (monitor.lookups, monitor, e))

            if instance in vars_query:
                monitors.append(monitor)
                values = vars_query.all()
                for value in values:
                    vars.append(value) if value not in vars else next

    context = {'vars': {}, 'var': {}}
    alarms = Alarm.objects.filter(monitor__in=monitors, monitor__active=True)
    for alarm in alarms:
        for var_item in vars:
            load = "{% load alarms_template_filters %}"
            context['vars'][var_item.slug] = var_item  # i.e -> {'food-al1': <Var: 'food-al1'>, 'food-other': <Var: 'food-other'>}
            context['var'] = var_item  # Current var
            # Evaluate the condition and take a boolean(True or False) if another result is another, nothing happens
            try:
                template = Template(load + alarm.formula)  # example -> {{ var.value }} > 12
                # Evaluate the condition and take a boolean(True or False) if another result is another, nothing happens
                condition = eval(template.render(Context(context)))
            except:
                print('Error evaluating formula of ' + alarm.name + ', variable: ' + var_item.slug)
                condition = None
                pass

            if condition == True:  # if formula evaluation return True
                variable = Var.objects.get(id=var_item.id)
                device = Device.objects.get(id=var_item.device.id)
                last_event = AlarmEvent.objects.filter(alarm=alarm, variables=variable, device=device).last()
                if last_event is not None:
                    new_date = last_event.created + timezone.timedelta(hours=alarm.duration)
                    if timezone.now() > new_date:
                        AlarmEvent.objects.create(alarm=alarm, variables=variable, device=device,
                                                  description=alarm.description)
                        print('Event created')
                else:
                    AlarmEvent.objects.create(alarm=alarm, variables=variable, device=device,
                                              description=alarm.description)
                    print('Event created')
            elif condition == False:  # if formula evaluation return False, NO CASE IF FORMULA FAULT
                # In this, we want to set finished date to the events with same var and device, don't have finished date
                # and because false, have a good value for variable.
                variable = Var.objects.get(id=var_item.id)
                device = Device.objects.get(id=var_item.device.id)
                AlarmEvent.objects.filter(alarm=alarm, variables=variable, device=device,
                                          finished=None).update(finished=timezone.now(), description=alarm.description)


@receiver(post_save, sender=Var)
def create_event_for_alarm_formula_looking_var_for_monitor_var_selection(sender, instance, **kwargs):

    """
    Create an event if var instance satisfy the condition in formula field of an alarm
    """
    # Only for alarms with monitors with selected variables in select box, and no with lookups
    alarms = Alarm.objects.filter(monitor__variables=instance, monitor__active=True, monitor__lookups="")
    context = {
        'vars': {instance.slug: {'slug': instance.slug, 'var_type': instance.var_type, 'value': instance.value,
                                 'device': instance.device}},
        'var': {'slug': instance.slug, 'value': instance.value, 'device': instance.device}
    }

    for alarm in alarms:
        condition = False
        try:
            template = Template(alarm.formula)  # example -> {{ vars.voltaje.value }} > 12
            condition = eval(template.render(Context(context)))  # eval the formula with values in context dictionary
        except:
            print('Error al ejecutar formula de alarma ' + alarm.name)
            break

        if condition == True:
            last_event = AlarmEvent.objects.filter(alarm=alarm, device=instance.device, variables=instance).last()
            if last_event is not None:
                new_date = last_event.created + timezone.timedelta(hours=alarm.duration)
                if timezone.now() > new_date:
                    AlarmEvent.objects.create(alarm=alarm, device=instance.device, variables=instance,
                                      description=alarm.description)
            else:
                AlarmEvent.objects.create(alarm=alarm, device=instance.device, variables=instance,
                                          description=alarm.description)
        elif condition == False:
            AlarmEvent.objects.filter(alarm=alarm, device=instance.device, variables=instance, finished=None).update(
                finished=timezone.now(), description=alarm.description)


def create_event_for_not_specific_model_and_signal(sender_instance, alarm_instance):

    """
    Create an event for not specific signal, setting the instance in ContentType field of event.
    This function should to be call by a post_save signal, to create an event with content_type field
    The signal should call the function and pass the object instance and the alarm instance
    :param sender_instance: Generic object
    :param alarm_instance: Alarm instance
    """
    context = {
        'var': sender_instance
    }
    # key 'var' take the object value, for this reason in alarm template,
    # user can access to any field of it. Remember that template execution should return True or False

    condition = False
    try:
        template = Template(alarm_instance.formula)
        condition = eval(template.render(Context(context)))
    except:
        print('Formula error: ' + alarm_instance.name)
        return

    if condition == True:   # Create the new event
        event = AlarmEvent.objects.create(alarm=alarm_instance)
        event.content_type = [sender_instance]
        event.save()
    if condition == False:  # Update finished date to event
        events = AlarmEvent.objects.filter(alarm=alarm_instance)
        for event in events:
            event.update(finished=timezone.now()) if list(event.content_type) == [sender_instance] else None

"""
# TODO: Remove this code from previous version
from django.core.mail import mail_managers
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.db.models import Q

from comm.models import Message

network_not_communicate = Signal(providing_args=['network'])  # Signal to indicate that a network is not communicate
device_not_communicate = Signal(providing_args=["device"])  # Signal to indicate that a device is not communicate
loss_message_write = Signal(providing_args=["devices", "messages"])
loss_message_read = Signal(providing_args=["messages"])

@receiver(network_not_communicate)
def send_notification_network_not_communicate(sender, network, **kwargs):
    params = {'network': network,
              'timeout': settings.COMM_NETWORK_DISCONNECT_TIME_ALARM,
              'site_domain': Site.objects.get_current().domain,
             }
    try:
        mail_managers(
            render_to_string('alarms/emails/user_network_not_communicate_notification_subject.txt', params),
            render_to_string('alarms/emails/user_network_not_communicate_notification_body.txt', params),
            fail_silently=False,
            html_message=render_to_string('alarms/emails/user_network_not_communicate_notification_body.html', params)
        )
        q_waiting = Q(status=Message.STATUS_WAITING_FOR_RESET)
        q_not_responded = Q(status=Message.STATUS_NOT_RESPONDED)
        q_sent = Q(status=Message.STATUS_SENT)
        q_send_at = Q(send_at__gte=network.last_comm)
        q_created = Q(created__gt=network.last_comm)
        Message.objects.filter((q_waiting | q_not_responded | q_sent) & (q_send_at | q_created),
                               network_id=network.id).update(status=Message.STATUS_ENQUEUED)
        network.not_connected_alarm = True
        network.save()

    except Exception as e:
        print "Details %s" % str(e)
"""
