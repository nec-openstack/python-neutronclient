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

from neutronclient.client import httpclient
from neutronclient.client import sessionclient
from neutronclient.client import utils


# FIXME(bklei): Should refactor this to use kwargs and only
# explicitly list arguments that are not None.
def construct_http_client(
        # username=None,
        # user_id=None,
        # tenant_name=None,
        # tenant_id=None,
        # password=None,
        # auth_url=None,
        # token=None,
        # region_name=None,
        timeout=None,
        # endpoint_url=None,
        # insecure=False,
        # endpoint_type='public',
        # log_credentials=None,
        auth_strategy='keystone',
        # ca_cert=None,
        # service_type='network',
        session=None,
        auth=None,
        # os-client-config
        cloud=None,
        argparse=None,
        **kwargs):

    if session:
        kwargs.setdefault('user_agent', 'python-neutronclient')
        kwargs.setdefault('interface', kwargs.get('endpoint_type'))
        return sessionclient.SessionClient(session=session,
                                           auth=auth,
                                           **kwargs)
    elif auth_strategy == 'keystone':
        cloud_config = utils.get_cloud_config(cloud, argparse, **kwargs)
        return utils.get_keystone_sessionclient(
            sessionclient.SessionClient,
            cloud_config, timeout)
    else:
        # auth_strategy == noauth
        # FIXME(bklei): username and password are now optional. Need
        # to test that they were provided in this mode.  Should also
        # refactor to use kwargs.
        return httpclient.HTTPClient(
            username=kwargs.get('username'),
            password=kwargs.get('password'),
            tenant_id=kwargs.get('tenant_id'),
            tenant_name=kwargs.get('tenant_name'),
            user_id=kwargs.get('user_id'),
            auth_url=kwargs.get('auth_url'),
            token=kwargs.get('token'),
            endpoint_url=kwargs.get('endpoint_url'),
            insecure=kwargs.get('insecure', False),
            timeout=kwargs.get('timeout'),
            region_name=kwargs.get('region_name'),
            endpoint_type=kwargs.get('endpoint_type', 'public'),
            service_type=kwargs.get('service_type', 'network'),
            ca_cert=kwargs.get('ca_cert'),
            log_credentials=kwargs.get('log_credentials'),
            auth_strategy=auth_strategy)
