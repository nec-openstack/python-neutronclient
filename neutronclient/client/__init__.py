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
from oslo_utils import importutils

from neutronclient._i18n import _
from neutronclient.client.base import construct_http_client
from neutronclient.client.httpclient import HTTPClient
from neutronclient.client.sessionclient import SessionClient
from neutronclient.common import exceptions


__all__ = (
    'construct_http_client',
    'HTTPClient',
    'SessionClient',
)


API_NAME = 'network'
API_VERSIONS = {
    '2.0': 'neutronclient.v2_0.client.Client',
    '2': 'neutronclient.v2_0.client.Client',
}


def get_client_class(api_name, version, version_map):
    """Returns the client class for the requested API version.

    :param api_name: the name of the API, e.g. 'compute', 'image', etc
    :param version: the requested API version
    :param version_map: a dict of client classes keyed by version
    :rtype: a client class for the requested API version
    """
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = _("Invalid %(api_name)s client version '%(version)s'. must be "
                "one of: %(map_keys)s")
        msg = msg % {'api_name': api_name, 'version': version,
                     'map_keys': ', '.join(version_map.keys())}
        raise exceptions.UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def Client(api_version,
           username=None,
           user_id=None,
           tenant_name=None,
           tenant_id=None,
           password=None,
           auth_url=None,
           region_name=None,
           token=None,
           endpoint_url=None,
           insecure=False,
           ca_cert=None,
           endpoint_type='public',
           # interface='public',
           service_type='network',
           # neutronclient specific
           log_credentials=None,
           auth_strategy='keystone',
           # keystoneauth1.session
           timeout=None,
           # retries=None,
           # raise_errors=None,
           # os-client-config
           cloud=None,
           argparse=None,
           # session=None,
           # auth=None,
           **kwargs):
    """Return a neutronclient object.

    :param api_version: Networking API version. 2.0 or 2 are valid.
    :param kwargs: any other parameter that can be passed to
        neutronclient.client.Client. All parameters supported in
        neutronclient.v2_0.client.ClientBase can be passed.
    """

    neutron_client = get_client_class(
        API_NAME,
        api_version,
        API_VERSIONS,
    )

    # NOTE: Ignore log_credentials. Use the default behavior of Session.
    if cloud is None:
        cloud = ''
    verify = kwargs.get('verify', not insecure)
    cert = kwargs.get('cert', ca_cert)

    interface = kwargs.get('interface', endpoint_type)
    if interface.endswith('URL'):
        interface = interface[:-3]
    kwargs['interface'] = interface

    config_params = kwargs.copy()
    if token and endpoint_url:
        config_params.setdefault('auth_type', 'admin_token')
        config_params['url'] = endpoint_url
        config_params['token'] = token

    cloud_config = os_client_config.OpenStackConfig().get_one_cloud(
        cloud=cloud,
        argparse=argparse,
        network_api_version=api_version,
        username=username,
        user_id=user_id,
        tenant_name=tenant_name,
        tenant_id=tenant_id,
        password=password,
        auth_url=auth_url,
        region_name=region_name,
        verify=verify,
        cert=ca_cert,
        **config_params)
    verify, cert = cloud_config.get_requests_verify_args()
    auth = cloud_config.get_auth()
    auth_session = ks_session.Session(auth=auth,
                                      verify=verify,
                                      cert=cert,
                                      timeout=timeout)

    kwargs.setdefault('user_agent', 'python-neutronclient')

    return neutron_client(
        session=auth_session,
        auth=auth,
        service_type=cloud_config.get_service_type('network'),
        service_name=cloud_config.get_service_name('network'),
        region_name=cloud_config.get_region_name(),
        auth_strategy=auth_strategy,
        endpoint_type=interface,
        **kwargs)
