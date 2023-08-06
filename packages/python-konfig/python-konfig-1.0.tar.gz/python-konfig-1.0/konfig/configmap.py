"""konfig is a library to make it simple to read and write config maps.

It uses the service account inside the pod to access the API and supports no
other way of reading the credentials. The library aims to solve the problem
that some applications have that they only need a relatively tiny amount of
storage that is rarely updated.

Example: Read / write the config map:

    import konfig

    configmap = konfig.configmap('test-config', namespace='default')
    myconfig = configmap.read()
"""

import os
import requests

SECRETS_PREFIX = '/run/secrets/kubernetes.io/serviceaccount/'


class ConfigMap(object):
    def __init__(self, name, namespace, server, token, capath):
        self.name = name
        self.namespace = namespace
        self.server = server
        self.token = token
        self.capath = capath

    def url(self):
        return '{server}/api/v1/namespaces/{ns}/configmaps/{name}'.format(
                name=self.name, ns=self.namespace, server=self.server)

    def _headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token,
        }

    def read(self):
        """Reads config map from Kubernetes.

        Returns:
          dict of the data in the config map.
        """
        response = requests.get(
                self.url(), headers=self._headers(), verify=self.capath)
        response.raise_for_status()
        return response.json().get('data', None)

    def update(self, data):
        """Updates config map on Kubernetes.

        Args:
          data: dict of the data to write to the config map.
        """
        obj = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
            },
            "data": {str(k): str(v) for k, v in data.items()},
        }
        response = requests.put(
                self.url(), headers=self._headers(), verify=self.capath,
                json=obj)
        response.raise_for_status()


def configmap(name, namespace=None, server=None):
    """Create a ConfigMap referring to a config map.

    Args:
      name: Name of the config map.
      namespace: Namespace name, or None in which case either
        KONFIG_NAMESPACE will be used if set or 'default'.
      server: Server URL, or None in which case either
        KONFIG_SERVER will be used if set or 'https://kubernetes.default'.

    Returns:
      ConfigMap instance.
    """
    namespace = namespace or (
            os.environ.get('KONFIG_NAMESPACE', 'default'))
    server = server or (
            os.environ.get('KONFIG_SERVER', 'https://kubernetes.default'))
    with open(os.path.join(SECRETS_PREFIX, 'token'), 'r') as f:
        token = f.read().strip()
    capath = os.path.join(SECRETS_PREFIX, 'ca.crt')
    return ConfigMap(name, namespace, server, token, capath)
