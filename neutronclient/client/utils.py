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

from keystoneauth1 import session as ks_session
import os_client_config


class OpenStackConfig(os_client_config.OpenStackConfig):

    def auth_config_hook(self, config):
        token = config.get('token')
        if 'endpoint_url' in config:
            config['endpoint'] = config.pop('endpoint_url')
        endpoint = config.get('endpoint') or config.get('url')
        if (token and endpoint):
            config['auth_type'] = 'admin_token'
            config['endpoint'] = endpoint
        return config


def get_cloud_config(cloud=None,
                     argparse=None,
                     **kwargs):

    config_params = kwargs.copy()

    if cloud is None:
        cloud = ''
    verify = config_params.get('verify',
                               not config_params.get('insecure', False))
    cert = config_params.get('cert',
                             config_params.get('ca_cert'))

    interface = config_params.get('interface',
                                  config_params.get('endpoint_type'))
    if interface and interface.endswith('URL'):
        interface = interface[:-3]

    config_params.setdefault('network_api_version',
                             config_params.get('api_version'))

    cloud_config = OpenStackConfig().get_one_cloud(
        cloud=cloud,
        argparse=argparse,
        verify=verify,
        cert=cert,
        interface=interface,
        **config_params)

    return cloud_config


def get_keystone_sessionclient(client_class, cloud_config, timeout, **kwargs):
    verify, cert = cloud_config.get_requests_verify_args()
    auth = cloud_config.get_auth()
    auth_session = ks_session.Session(auth=auth,
                                      verify=verify,
                                      cert=cert,
                                      timeout=timeout)
    kwargs.setdefault('user_agent', 'python-neutronclient')
    return client_class(
        session=auth_session,
        auth=auth,
        region_name=cloud_config.get_region_name(),
        service_type=cloud_config.get_service_type('network'),
        service_name=cloud_config.get_service_name('network'),
        interface=cloud_config.get_interface('network'),
        **kwargs)
