import requests
import json
from .config import get_config


def put(uri, method, body, token):
    if method == 'PUT':
        request_method = requests.put
    elif method == 'POST':
        request_method = requests.post
    else:
        raise Exception('ERROR: Unsupported method [{}]'.format(method))

    result = request_method(uri,
                          data=json.dumps(body),
                          headers={
                             'Accept': 'application/json',
                             'Content-Type': 'application/json',
                            # 'Authorization': 'Bearer {}'.format(token)
                          },
                          cookies={'oidc_id_token': token}
    )
    return result


def get_api_root():
    config = get_config()
    api_domain = config['datalake']['datacat_url']
    return api_domain


class SirenAction:
    def __init__(self, dict):
        api_root = get_api_root()

        self.__dict__ = dict
        self.api_root = api_root

    def execute(self, token, body=None, substitutions=None):
        uri = '{}{}'.format(self.api_root, self.href)

        if substitutions:
            for k, v in substitutions.items():
                uri = uri.replace(k, v)

        response = put(uri, self.method, body, token)
        return response


class SirenEntity:
    def __init__(self, data):
        api_root = get_api_root()

        self.__dict__ = data
        self.api_root = api_root

    @classmethod
    def fetch_from(cls, url, token):
        if not url.startswith('http'):
            url = '{}{}'.format(get_api_root(), url)
        response = requests.get(url, cookies={'oidc_id_token': token})
        if response.status_code != 200:
            raise Exception("ERROR: Cannot connect to [{}] response: [{}]".format(url, response.status_code))
        return cls(response.json())

    def get_action(self, name):
        actions = list(filter(lambda action: action['name'] == name, self.actions))
        if not actions:
            return None
        if len(actions) > 1:
            raise ValueError("Error: multiple matching actions found!")

        return SirenAction(actions[0])


def register_package(token, metadata):
    return SirenEntity.fetch_from('/__api/', token).get_action('add-package').execute(token, body={'properties': metadata})


def register_dataset(token, package_id, metadata):
    get_package_action = SirenEntity.fetch_from('/__api/', token).get_action('get-package')
    uri = '{}{}'.format(get_package_action.api_root, get_package_action.href.replace('__package_id__', package_id))
    return SirenEntity \
        .fetch_from(uri, token) \
        .get_action('add-dataset') \
        .execute(token, body={'properties': metadata})

