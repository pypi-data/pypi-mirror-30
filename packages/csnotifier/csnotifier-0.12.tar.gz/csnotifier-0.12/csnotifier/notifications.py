from django.conf import settings

import json
import requests

PUSHWOOSH_APP_ID = getattr(settings, 'PUSHWOOSH_APP_ID', '')
PUSHWOOSH_AUTH_TOKEN = getattr(settings, 'PUSHWOOSH_AUTH_TOKEN', '')
PUSHWOOSH_URL = getattr(settings, 'PUSHWOOSH_URL', 'https://cp.pushwoosh.com/json/1.3/createMessage') # noqa
FIREBASE_API_KEY = getattr(settings, 'FIREBASE_API_KEY', '')
FIREBASE_URL = getattr(settings, 'FIREBASE_URL', '')


def _create__pushwoosh_message(devices, notification):
    message = {
        'request': {
            'application': PUSHWOOSH_APP_ID,
            'auth': PUSHWOOSH_AUTH_TOKEN,
            'notifications': [{
                'send_date': 'now',
                'content': notification.getTitle(),
                'data': notification.getExtra(),
                'devices': devices
            }]
        }
    }
    return message


def _create__firebase_message(devices, notification):
    message = {
        "notification": {
            "title": notification.getTitle(),
            "body": notification.getDesc(),
            "sound": "default",
            "click_action": "FCM_PLUGIN_ACTIVITY",
            "icon": "fcm_push_icon"
        },
        "data": notification.getExtra(),
        "priority": "high",
    }

    if len(devices) == 1:
        message['to'] = devices[0]
    else:
        message['registration_ids'] = devices

    return message


def send_request(devices, notification):
    if PUSHWOOSH_APP_ID:
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(_create__pushwoosh_message(devices, notification))
        response = requests.post(
            PUSHWOOSH_URL,
            payload.encode('utf8'),
            headers=headers)
    else:
        headers = {
            'Authorization': 'key=' + FIREBASE_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = json.dumps(_create__firebase_message(devices, notification))
        response = requests.post(FIREBASE_URL, payload.encode('utf8'), headers=headers)

    if response and response.status_code == 200:
        return response.json()
    else:
        return {}
