from .DliRequestFactoryFactory import DliRequestFactoryFactory
from pypermedia import HypermediaClient
import requests


def _get_auth_key(ctx):
    key = ctx.api_key
    auth_header = "Bearer {}".format(key)
    start_session_url = "{}/start-session".format(ctx.api_root)  # TODO: Siren
    r = requests.post(start_session_url, headers={"Authorization": auth_header})

    return r.text


class Ctx(object):
    def __init__(self, api_key, api_root):
        self.api_key = api_key
        self.api_root = api_root
        self.auth_key = _get_auth_key(self)
        self.request_factory = DliRequestFactoryFactory(api_root, lambda: self.get_header_with_auth()).request_factory
        self.s3_keys = {}

    def get_header_with_auth(self):
        auth_header = "Bearer {}".format(self.auth_key)
        return {"Authorization": auth_header}

    def uri_with_root(self, relative_path):
        return "{}/{}".format(self.api_root, relative_path)

    def get_root_siren(self):
        return HypermediaClient.connect(self.api_root, request_factory=self.request_factory)
