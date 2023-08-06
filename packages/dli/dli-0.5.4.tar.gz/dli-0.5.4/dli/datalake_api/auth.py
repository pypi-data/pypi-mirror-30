from .config import get_config
import requests
import urllib.parse
import uuid

def authenticate():
    return 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImlhdCI6MTUxMzMzMTUwOSwiZXhwIjo5NTEzMzM1MTA5fQ.eyJhdWQiOiJkYXRhbGFrZS1hY2NvdW50cyIsImF1dGhfdGltZSI6MTUxMzMzMTUwOSwiZGF0YWxha2UiOnsiYWNjb3VudHMiOnsiaWJveHgiOiJydyIsIm1yZCI6InIifX0sImVtYWlsIjoiamltQGV4YW1wbGUuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImV4cCI6OTUxMzMzNTEwOSwiaWF0IjoxNTEzMzMxNTA5LCJpc3MiOiJodHRwczovL2h5ZHJhLWRldi51ZHBtYXJraXQubmV0Iiwibm9uY2UiOiI1YTgyMzI2NC1iN2QzLTQ4NWUtYjc2MS1lYzE1MTI5NDQ4MTQiLCJzdWIiOiJ1c2VyOjEyMzQ1OmppbSJ9.6P5AdICdJDtS-jFX7XjcvM5d8XTfyWlfe2d1HOpx1rY'

    #TODO: API KEY exchange!

# def authenticate():
#     config = get_config()
#
#     auth_point = config['hydra']['auth_url']
#
#     client = 'datalake-test' #config['hydra']['client']
#
#     username = config['user']['username']
#     password = config['user']['password']
#
#     auth_request = '{}?client_id={}&state={}&redirect_uri={}&scope=openid+hydra.introspect+email&access_type=offline&response_type=token+id_token'.format(
#         auth_point,
#         client,
#         str(uuid.uuid4()),
#         urllib.parse.quote_plus('http://localhost:5000/oidc_callback')
#     )
#     print(auth_request)
#
#     # initiating call to hydra
#     response = requests.get(auth_request, allow_redirects=False)
#     consent_url = response.headers['Location']
#     hydra_cookie = response.cookies
#     print(consent_url)
#     # redirect to consent app
#     response = requests.get(consent_url, allow_redirects=False)
#     split = urllib.parse.urlsplit(consent_url)
#     login_url = "{0.scheme}://{0.netloc}{1}".format(split, response.headers['Location'])
#     consent_token = list(filter(lambda x: x.startswith('consent'), split.query.split('&')))[0].replace('consent=', '')
#
#     # redirect to IDP
#     response = requests.post(login_url,
#                              allow_redirects=False,
#                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
#                              data={'username': username, 'password': password, 'consent': consent_token})
#
#     idp_cookie = response.cookies
#     new_url = "{0.scheme}://{0.netloc}{1}".format(split, response.headers['Location'])
#
#     # redirect to consent app
#     response = requests.get(new_url, allow_redirects=False, cookies=idp_cookie)
#
#     # redirect back to hydra
#     response = requests.get(response.headers['Location'], allow_redirects=False, cookies=hydra_cookie)
#     redirect_url = response.headers['Location']
#     print(redirect_url)
#     tokens = {p[0]: p[1] for p in [t.split('=') for t in urllib.parse.urlsplit(redirect_url).fragment.split('&') if 'token' in t]}
#
#     response = requests.get(redirect_url, allow_redirects=False)
#     print(response)
#
#     resp = requests.get('http://localhost:5000/introspection',
#                         allow_redirects=False,
#                         headers={'Cookies': 'oidc_id_token=' + tokens['id_token']})
#     print(resp)
#     return tokens