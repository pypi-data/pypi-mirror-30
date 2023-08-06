import boto3
from configparser import ConfigParser
import configparser

from vital.cache import cached_property, memoize


@memoize
def get_session(**credentials):
    return boto3.session.Session(**credentials)


class AwsManager(object):

    def __init__(self, session=None, boto_cfg='/etc/boto.cfg',
                 policy_name='default'):
        self._cfg = boto_cfg
        self.policy = policy_name
        self._session = session

    @cached_property
    def cfg(self):
        cfg = ConfigParser()
        try:
            with open(self._cfg) as f:
                cfg = ConfigParser()
                cfg.read_file(f)
        except:
            pass
        return cfg

    @property
    def session(self):
        if not self._session:
            aid = None
            sk = None
            if self.access_id is not None:
                aid = self.access_id.decode()
            if self.secret_key is not None:
                sk = self.secret_key.decode()
            return get_session(aws_access_key_id=aid,
                               aws_secret_access_key=sk,
                               region_name=self.region_name)

    @property
    def region_name(self):
        try:
            return self.cfg.get(self.policy, 'region').encode()
        except (AttributeError, configparser.NoOptionError,
                configparser.NoSectionError):
            return 'us-east-1'

    @property
    def secret_key(self):
        try:
            return self.cfg.get(self.policy, 'aws_secret_access_key').encode()
        except (AttributeError, configparser.NoSectionError,
                configparser.NoOptionError):
            return None

    @property
    def access_id(self):
        try:
            return self.cfg.get(self.policy, 'aws_access_key_id').encode()
        except (AttributeError, configparser.NoSectionError,
                configparser.NoOptionError):
            return None

    @cached_property
    def resource(self):
        return self.session.resource(self.RESOURCE_NAME)

    @cached_property
    def client(self):
        return self.session.client(self.CLIENT_NAME, self.region_name)
