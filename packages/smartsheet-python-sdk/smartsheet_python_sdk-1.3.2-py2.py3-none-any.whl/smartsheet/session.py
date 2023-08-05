# Smartsheet Python SDK.
#
# Copyright 2016 Smartsheet.com, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# pylint: disable=no-member
# known issue regarding ssl module and pylint.

import ssl
import certifi

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import Retry


_TRUSTED_CERT_FILE = certifi.where()


class _SSLAdapter(HTTPAdapter):
    def create_ssl_context(self):
        ctx = ssl.create_default_context()
        ctx.options |= ssl.OP_NO_SSLv2
        ctx.options |= ssl.OP_NO_SSLv3
        ctx.options |= ssl.OP_NO_TLSv1
        return ctx

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       cert_reqs=ssl.CERT_REQUIRED,
                                       ca_certs=_TRUSTED_CERT_FILE,
                                       ssl_context=self.create_ssl_context())


def pinned_session(pool_maxsize=8):
    http_adapter = _SSLAdapter(pool_connections=4,
                               pool_maxsize=pool_maxsize,
                               max_retries=Retry(total=1,
                                                 method_whitelist=Retry.DEFAULT_METHOD_WHITELIST.union(['POST'])))

    _session = requests.session()
    _session.hooks = {'response': redact_token}
    _session.mount('https://', http_adapter)

    return _session


def redact_token(res, *args, **kwargs):
    if 'Authorization' in res.request.headers:
        res.request.headers.update({'Authorization': '[redacted]'})
    return res
