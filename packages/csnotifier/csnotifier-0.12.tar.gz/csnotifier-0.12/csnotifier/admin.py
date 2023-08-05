from csnotifier.models import Device
from csnotifier.models import Notification
from django import forms
from django.contrib import admin

from django.contrib.admin.helpers import ActionForm


class UpdateActionForm(ActionForm):
    device = forms.CharField(
        label='Device ID',
        help_text='Enter the devide id where the notification will be sent',
        required=False)


def mark_as_sent(modeladmin, request, queryset):
    queryset.update(sent=True)


mark_as_sent.short_description = "Mark these notifications as SENT"


def mark_as_not_sent(modeladmin, request, queryset):
    queryset.update(sent=False)


mark_as_not_sent.short_description = "Mark these notifications as NOT SENT"


def send_to_device(modeladmin, request, queryset):
    for item in queryset:
        item.send_to_device(request.POST.get('device'))


send_to_device.short_description = "Send notification to a device"


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'tags', 'data', 'sent')
    actions = [mark_as_sent, mark_as_not_sent, send_to_device]
    action_form = UpdateActionForm


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'tags', 'enabled', 'added', 'modified')
    ordering = ('-modified',)


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Device, DeviceAdmin)
