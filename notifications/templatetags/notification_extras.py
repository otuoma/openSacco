from django import template
from notifications.models import Notification

register = template.Library()


@register.filter(name='get_unread_msgs')
def get_unread_msgs(user):

    return Notification.objects.filter(read=False, to=user).count()


@register.filter(name='multiply')
def multiply(value, arg):

    return arg*value
