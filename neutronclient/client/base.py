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


# FIXME(bklei): Should refactor this to use kwargs and only
# explicitly list arguments that are not None.
def construct_http_client(username=None,
                          user_id=None,
                          tenant_name=None,
                          tenant_id=None,
                          password=None,
                          auth_url=None,
                          token=None,
                          region_name=None,
                          timeout=None,
                          endpoint_url=None,
                          insecure=False,
                          endpoint_type='public',
                          log_credentials=None,
                          auth_strategy='keystone',
                          ca_cert=None,
                          service_type='network',
                          session=None,
                          # os-client-config
                          cloud=None,
                          argparse=None,
                          **kwargs):

    if session:
        kwargs.setdefault('user_agent', 'python-neutronclient')
        kwargs.setdefault('interface', endpoint_type)
        return sessionclient.SessionClient(session=session,
                                           service_type=service_type,
                                           region_name=region_name,
                                           **kwargs)
    else:
        # auth_strategy == noauth
        # FIXME(bklei): username and password are now optional. Need
        # to test that they were provided in this mode.  Should also
        # refactor to use kwargs.
        return httpclient.HTTPClient(username=username,
                                     password=password,
                                     tenant_id=tenant_id,
                                     tenant_name=tenant_name,
                                     user_id=user_id,
                                     auth_url=auth_url,
                                     token=token,
                                     endpoint_url=endpoint_url,
                                     insecure=insecure,
                                     timeout=timeout,
                                     region_name=region_name,
                                     endpoint_type=endpoint_type,
                                     service_type=service_type,
                                     ca_cert=ca_cert,
                                     log_credentials=log_credentials,
                                     auth_strategy=auth_strategy)
