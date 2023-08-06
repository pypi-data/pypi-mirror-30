"""OpenHlTest Restconf transport
"""

import sys
import os
import ssl
import time
import json
import requests
import urllib3

if sys.version < '2.7.9':
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
else:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HttpTransport(object):
    """OpenHlTest Restconf transport."""

    def __init__(self, hostname, rest_port=443):
        """ Setup the https connection parameters to a rest server

        Args:
            hostname: hostname or ip address
            rest_port: the rest port of the host
        """
        self._headers = {}
        self._verify_cert = False
        self.trace = False
        self._scheme = 'https'
        self._connection = '%s://%s:%s' % (self._scheme, hostname, rest_port)

    @property
    def trace(self):
        """True/False to trace all http commands and responses."""
        return self._trace
    @trace.setter
    def trace(self, value):
        self._trace = value

    def get_object(self, target):
        response = self._send_recv('GET', target.url)
        self._populate_target(response, target)
        return target

    def create_object(self, parent, target, arg_dict):
        object_key = '%s:%s' % (target.YANG_MODULE, target.YANG_CLASS)
        payload = { object_key: {} }
        for key in arg_dict.keys():
            if key == 'self':
                continue
            payload[object_key][key] = arg_dict[key]
        location = self._send_recv('POST', parent.url, payload)
        return self.get_object(target)

    def update_object(self, url, payload):
        return self._send_recv('PATCH', url, payload)

    def delete_object(self, url, payload=None):
        return self._send_recv('DELETE', url, payload)

    def _print_trace(self, * args):
        if self.trace is True:
            print('%s %s' % (int(time.time()), ' '.join(args)))
        
    def _send_recv(self, method, url, payload=None, fid=None, file_content=None):
        headers = self._headers
        if url.startswith(self._scheme) == False:
            url = '%s/%s' % (self._connection, url.strip('/'))

        self._print_trace(method, url)
        
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            response = requests.request(method, url, data=json.dumps(payload), headers=headers, verify=self._verify_cert)
        elif method == 'POST' and fid is not None:
            headers['Content-Type'] = 'application/octet-stream'
            if fid.__class__.__name__ == 'BufferedReader':
                headers['Content-Length'] = os.fstat(fid.raw.fileno()).st_size
                response = requests.request(method, url, data=fid.raw, headers=headers, verify=self._verify_cert)
            else:                            
                response = requests.request(method, url, data=fid, headers=headers, verify=self._verify_cert)
        elif method == 'POST' and file_content is not None:
            headers['Content-Type'] = 'application/octet-stream'
            response = requests.request(method, url, data=json.dumps(file_content), headers=headers, verify=self._verify_cert)
        else:
            response = requests.request(method, url, data=None, headers=headers, verify=self._verify_cert)

        while(response.status_code == 202):
            self._print_trace('GET', response.headers['Location'])
            response = requests.request('GET', response.headers['Location'], verify=self._verify_cert)
            time.sleep(1)
            
        if response.status_code == 201:
            return response.headers['Location']
        elif response.status_code == 204:
            return None
        elif str(response.status_code).startswith('2') is True:
            if response.headers.get('Content-Type'):
                if 'application/json' in response.headers['Content-Type']:
                   return response.json()
            return None
        else:
            raise Exception('%s %s %s' % (response.status_code, response.reason, response.text))

    def _populate_target(self, payload, target):
        if isinstance(payload, list):
            target_list = []
            for item in payload:
                target_item = self._populate_target(item, target.__class__())
                target_list.append(target_item)
            return target_list
        elif isinstance(payload, dict):
            for key in payload.keys():
                if target.YANG_MODULE in key and target.YANG_CLASS in key:
                    target._values = payload[key]
                else:
                    target._values[key] = payload[key]
            return target
        else:
            raise Exception('unsupported payload type')

