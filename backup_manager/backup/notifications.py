import requests
import json
from backup_manager.secrets.secrets import SecretsManager
from backup_manager.backup.errors import NotificationError

PUSHBULLET_PUSH_URL = 'https://api.pushbullet.com/v2/pushes'


def send_notification(title, body):
    msg = {"type": "note", "title": title, "body": body}
    config_manager = SecretsManager()
    token = config_manager.pushbullet_token

    if token is None:
        raise NotificationError('pushbullet retrieving error')
    else:
        resp = requests.post(PUSHBULLET_PUSH_URL,
                             data=json.dumps(msg),
                             headers={'Authorization': 'Bearer {}'.format(token),
                                      'Content-Type': 'application/json'})

        if resp.status_code != 200:
            raise NotificationError('pushbullet notification error', resp.status_code)
        else:
            print('Message sent')
