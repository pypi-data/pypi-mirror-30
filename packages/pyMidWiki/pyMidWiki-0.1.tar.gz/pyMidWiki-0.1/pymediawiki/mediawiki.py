"""
The Module is meant to industrialise some of the repetitive work that you have to do while trying to communicate with
MediaWiki API. It uses requests (http://docs.python-requests.org)
"""

import json
import requests


class MediaWiki(object):
    """Used to gather most informations that will be used for every requests."""
    def __init__(self, headers, proxies, url):
        """
        A MediaWiki object will contain a requests.Session() so there will be no problem once you logged in.
        :param headers: dictionnary for passing headers (User-Agent, ...)
        :param proxies: dictionnary for proxies. It defaults to {'http': '', 'https': ''}
        :param url: the top-level URL of your wiki's API (i.e. http://mediawiki.com/api.php)
        """
        self.session = requests.Session()
        self.headers = headers
        self.proxies = proxies
        self.url = url

    def get_token(self, action):
        """
        Gets a new token corresponding to the action given as argument.
        :param action: a string that tells mediawiki why are we gathering a token
        :return: the answer of the API in json format.
        """
        base = self.url
        try:
            print("getting token for %s" % action)
            params = {'action': 'query', 'meta': 'tokens', 'type': action, 'format': 'json'} \
                if action is not 'query' \
                else {'action': 'query', 'meta': 'tokens', 'format': 'json'}
            login = self.session.get(
                    url=base,
                    params=params,
                    headers=self.headers,
                    proxies=self.proxies
            )
            return login.text
        except (ConnectionError, ValueError) as e:
            raise e

    def login(self, uname, pw):
        """
        Log in to the API
        :param uname: username to authenticate
        :param pw: password for the username
        :return: MediaWiki's answer in json format.
        """
        base = self.url
        try:
            token = json.loads(self.get_token('login'))["query"]["tokens"]["logintoken"]
            params = {
                'action': 'clientlogin',
                'username': uname,
                'password': pw,
                'format': 'json',
                'loginreturnurl': base,
            }
            data = {
                'logintoken': token
            }
            print("trying to login...")
            log = self.session.post(
                    url=base,
                    params=params,
                    headers=self.headers,
                    proxies=self.proxies,
                    data=data
            )
            return log.text
        except (ConnectionError, ValueError) as e:
            raise e

    def edit(self, text, params, uname, password):
        """
        Create or edit a page existing in the wiki
        :param text: the new content of the page as a string.
        :param params: a dictionnary containing information for the page. 'title' and 'format' are required, at least.
        :param uname: username to log in to the API
        :param password: password of the user.
        :return: MediaWiki's answer when trying to update the page.
        """
        base = self.url
        try:
            if not "error" in self.login(uname, password):
                token = json.loads(self.get_token('query'))["query"]["tokens"]["csrftoken"]
                params = {
                    'action': 'edit',
                    'title': params["title"],
                    'format': params["format"]
                }
                data = {
                    'text': text,
                    'token': token,
                }
                req = self.session.post(
                        url=base,
                        params=params,
                        headers=self.headers,
                        proxies=self.proxies,
                        data=data
                )
            else:
                raise AuthenticationError()
        except (ConnectionError, ValueError) as e:
            raise e


class AuthenticationError(Exception):
    """Raised when login fails."""
    def __init__(self):
        super().__init__("Invalid Username or Password")
