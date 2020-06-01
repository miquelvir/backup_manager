from configparser import ConfigParser
from backup_manager.common import SECRETS_PATH

PUSHBULLET_KEY = "pushbullet"
TOKEN_KEY = "token"


class SecretsManager:
    def __init__(self):
        self._configuration = ConfigParser()
        self._configuration.read(SECRETS_PATH)

    @property
    def pushbullet_token(self):
        try:
            return self._configuration.get(PUSHBULLET_KEY, TOKEN_KEY)
        except KeyError:
            return ""

    @pushbullet_token.setter
    def pushbullet_token(self, value: str):

        assert type(value) == str

        try:
            self._configuration.set(PUSHBULLET_KEY, TOKEN_KEY, value)
            self._save()
        except (IOError, KeyError):
            raise

    @pushbullet_token.deleter
    def pushbullet_token(self):
        try:
            self._configuration.remove_option(PUSHBULLET_KEY, TOKEN_KEY)
            self._save()
        except (IOError, KeyError):
            raise

    def _save(self):
        try:
            with open(SECRETS_PATH, 'w') as configfile:
                self._configuration.write(configfile)
        except IOError:
            raise
