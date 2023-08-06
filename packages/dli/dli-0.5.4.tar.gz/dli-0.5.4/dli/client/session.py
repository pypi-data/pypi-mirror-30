from .DliClient import DliClient

import urllib3
import requests

urllib3.disable_warnings()


def start_session(api_key, root_url):
    client = DliClient(api_key, root_url)
    return client

def test_something_a(ctx):
    url = ctx.uri_with_root('something-a')
    res = requests.get(url, headers=ctx.get_header_with_auth())
    print("fooo")
    print(res.text)
    print(res)
