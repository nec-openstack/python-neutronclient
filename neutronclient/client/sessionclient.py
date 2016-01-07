#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

from keystoneauth1 import adapter
import requests

from neutronclient.common import exceptions


MAX_URI_LEN = 8192


class SessionClient(adapter.Adapter):

    def request(self, *args, **kwargs):
        kwargs.setdefault('authenticated', False)
        kwargs.setdefault('raise_exc', False)

        content_type = kwargs.pop('content_type', None) or 'application/json'

        headers = kwargs.setdefault('headers', {})
        headers.setdefault('Accept', content_type)

        try:
            kwargs.setdefault('data', kwargs.pop('body'))
        except KeyError:
            pass

        if kwargs.get('data'):
            headers.setdefault('Content-Type', content_type)

        resp = super(SessionClient, self).request(*args, **kwargs)
        return resp, resp.text

    def _check_uri_length(self, url):
        uri_len = len(self.endpoint_url) + len(url)
        if uri_len > MAX_URI_LEN:
            raise exceptions.RequestURITooLong(
                excess=uri_len - MAX_URI_LEN)

    def do_request(self, url, method, **kwargs):
        kwargs.setdefault('authenticated', True)
        self._check_uri_length(url)
        try:
            return self.request(url, method, **kwargs)
        except requests.exceptions.ConnectionError as e:
            # For backward compatibility with HTTPClient
            raise exceptions.ConnectionFailed(reason=e)

    @property
    def endpoint_url(self):
        # NOTE(jamielennox): This is used purely by the CLI and should be
        # removed when the CLI gets smarter.
        return self.get_endpoint()

    @property
    def auth_token(self):
        # NOTE(jamielennox): This is used purely by the CLI and should be
        # removed when the CLI gets smarter.
        return self.get_token()

    def authenticate(self):
        # NOTE(jamielennox): This is used purely by the CLI and should be
        # removed when the CLI gets smarter.
        self.get_token()

    def get_auth_info(self):
        auth_info = {'auth_token': self.auth_token,
                     'endpoint_url': self.endpoint_url}

        # NOTE(jamielennox): This is the best we can do here. It will work
        # with identity plugins which is the primary case but we should
        # deprecate it's usage as much as possible.
        try:
            get_access = (self.auth or self.session.auth).get_access
        except AttributeError:
            pass
        else:
            auth_ref = get_access(self.session)

            auth_info['auth_tenant_id'] = auth_ref.project_id
            auth_info['auth_user_id'] = auth_ref.user_id

        return auth_info
