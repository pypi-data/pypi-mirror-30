from .notifications import send_request
from django.conf import settings
from django.db import models

import json
import uuid


class DeviceManager(models.Manager):
    def register_device(self, token):
        device_id = uuid.uuid4().get_hex().replace('-', '')
        device = Device.objects.filter(token=token).first()
        if device is not None:
            return device
        else:
            return Device.objects.create(uuid=device_id, token=token)


    def enabled(self):
        return super(DeviceManager, self).get_queryset().filter(enabled=True)

    def search(self, target_notification):
        # Pre django code
        match = []
        tags_string = target_notification.getTags()
        if tags_string is None:
            return list(Device.objects.enabled())
        filter_elements = tags_string.split(',')
        for device in Device.objects.enabled():

            d_tags = device.getTags()
            if d_tags is not None:
                d_tags = d_tags.strip()
            else:
                d_tags = u''
            if not d_tags:
                 # if tags is an empty string, the device is subscribed to everything.
                match.append(device)
            else:
                for elem in filter_elements:
                    if elem in d_tags and device not in match:
                        match.append(device)
        return match


class Device(models.Model):
    uuid = models.CharField(max_length=32, primary_key=True)
    token = models.CharField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    tags = models.TextField()
    enabled = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now=True, blank=True)

    def disableNotifications(self):
        self.enabled = False
        self.save()

    def setTags(self, tag_string):
        self.tags = tag_string
        self.save()

    def setStatus(self, status):
        self.enabled = status
        self.save()

    def getTags(self):
        return self.tags

    def getToken(self):
        return self.token

    def getUuid(self):
        return self.uuid

    def __unicode__(self):
        return self.uuid

    objects = DeviceManager()


class Notification(models.Model):
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=250, blank=True, null=True)
    extra_context = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    sent = models.BooleanField(default=False)
    data = models.DateTimeField(auto_now_add=True)
    pw_status = models.SmallIntegerField(null=True, blank=True)
    pw_status_message = models.CharField(max_length=255, null=True, blank=True)
    pw_response = models.TextField(blank=True, null=True)

    def getTitle(self):
        return self.title

    def getDesc(self):
        return self.desc

    def setTags(self, tag_string):
        self.tags = tag_string
        self.save()

    def getTags(self):
        return self.tags

    def getTargetDevices(self):
        return []

    def setSent(self):
        self.sent = True
        self.save()

    def isSent(self):
        return self.sent

    def getData(self):
        return self.data

    def setExtra(self, data_dict):
        try:
            to_json = json.dumps(data_dict)
        except:
            to_json = ''
        self.extra_context = to_json
        self.save()

    def getExtra(self):
        try:
            load_context = json.loads(self.extra_context)
        except:
            load_context = {}
        return load_context

    def send(self):
        if self.isSent() is False:
            devices_token = set()
            devices = Device.objects.search(self)
            for device in devices:
                devices_token.add(device.getToken())
            if len(devices_token) > 0:
                status = send_request(list(devices_token), self)

                if 'status_code' in status:
                    self.pw_status = status.get('status_code')
                    self.pw_status_message = status.get('status_message')
                    self.pw_response = json.dumps(status.get('response'))
                else:
                    self.pw_status = status.get('success') >= 1 and 200 or None
                    self.pw_response = status
                if self.pw_status == 200:
                    self.sent = True
                self.save()
        return self

    def send_to_device(self, deviceid):
        devices = Device.objects.filter(uuid=deviceid)
        device_tokens = []
        for device in devices:
            token = device.getToken()
            device_tokens.append(token)
        status = send_request(device_tokens, self)
        return self

"""
    def save(self, *args, **kwargs):
        if self.isSent() is False:
            self.send()
        super(Notification, self).save(*args, **kwargs)
"""
