# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import json
import pickle
import os

import requests
from requests.auth import HTTPBasicAuth
from six.moves.urllib.parse import quote
from six import PY3


class APICallError(Exception):
    def __str__(self, *args, **kwargs):
        if PY3:
            return super(APICallError, self).__str__(*args, **kwargs)
        return self.message


class AWSFederationClientCmd(object):
    """Class for a command line client which uses the afp api"""

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')

        self.api_url = kwargs.get('api_url', None)
        self.ssl_verify = kwargs.get('ssl_verify', True)

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'afp-cli/1.0.6'})

        self.user_config_dir = os.path.expanduser("~/.afp-cli")
        self.cookie_filepath = os.path.join(self.user_config_dir, 'cookies')
        if os.path.exists(self.cookie_filepath):
            cookies = pickle.load(open(self.cookie_filepath, 'rb'))
            self.session.cookies = cookies

    def call_api(self, url_suffix):
        """Send a request to the aws federation proxy"""
        url_orig = '{0}{1}'.format(self.api_url, url_suffix)
        url = requests.utils.requote_uri(url_orig)
        # TODO: Automatic versioning instead of the static below
        api_result = self.session.get(
            url, verify=self.ssl_verify,
            auth=HTTPBasicAuth(self.username, self.password))
        if api_result.status_code != 200:
            if api_result.status_code == 401:
                # Need to treat 401 specially since it is directly send
                # from webserver and body has different format.
                raise APICallError("API call to AWS url (%s) failed: %s %s" % (
                    url_orig, api_result.status_code, api_result.reason))
            else:
                try:
                    raise APICallError("API call to AWS (%s) failed: %s" % (
                        url_orig, api_result.json()['message']))
                except ValueError:
                    raise APICallError("API call to AWS (%s) failed: %s" % (
                        url_orig, api_result.text))

        if not os.path.exists(self.user_config_dir):
            os.mkdir(self.user_config_dir)
        pickle.dump(self.session.cookies, open(self.cookie_filepath, 'wb'))
        return api_result.text

    def get_account_and_role_list(self):
        """Create an aws federation proxy request and return the result"""
        accounts_and_roles = self.call_api("/account")
        return json.loads(accounts_and_roles)

    def get_aws_credentials(self, account, role):
        """Return AWS credentials for a specified user and account"""
        aws_credentials = self.call_api(
            "/account/{0}/{1}".format(quote(account), quote(role)))
        aws_credentials = json.loads(aws_credentials)
        return {'AWS_ACCESS_KEY_ID': aws_credentials['AccessKeyId'],
                'AWS_SECRET_ACCESS_KEY': aws_credentials['SecretAccessKey'],
                'AWS_SESSION_TOKEN': aws_credentials['Token'],
                'AWS_SECURITY_TOKEN': aws_credentials['Token'],
                'AWS_EXPIRATION_DATE': aws_credentials['Expiration']}
