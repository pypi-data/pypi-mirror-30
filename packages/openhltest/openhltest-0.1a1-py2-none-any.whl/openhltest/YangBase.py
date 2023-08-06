from HttpTransport import HttpTransport

class YangBase(object):
    def __init__(self, parent, yang_key_value):
        self._values = {}
        self._dirty = []

        if isinstance(parent, HttpTransport) is True:
            self._http_transport = parent
            self._rest_path = '/restconf/data'
        else:
            self._http_transport = parent._http_transport
            module = self.YANG_MODULE
            self._rest_path = parent.url
            if self._rest_path.endswith('/') is False:
                self._rest_path += '/'
            if (self.YANG_MODULE in self._rest_path) is False:
                self._rest_path += self.YANG_MODULE + ':'
            self._rest_path += self.YANG_CLASS
        if yang_key_value is not None:
            self._rest_path = '%s=%s' % (self._rest_path, yang_key_value)

    @property
    def url(self):
        return self._rest_path

    @property
    def transport(self):
        return self._http_transport

    def dump(self):
        print('object: %s' % self.url)
        for key in self._values.keys():
            print('\t%s: %s' %(key, self._values[key]))
            
    def _get_value(self, key):
        if key in self._values.keys():
            return self._values[key]
        else:
            return None

    def _set_value(self, key, value):
        self._values[key] = value
        self._dirty.append(key)

    def update(self, description=None):
        '''Update the object with any values that are dirty.'''
        return self._restconf.update(self)