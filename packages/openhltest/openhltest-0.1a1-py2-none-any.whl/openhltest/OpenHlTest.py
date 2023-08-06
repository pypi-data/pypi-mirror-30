from HttpTransport import HttpTransport
from YangBase import YangBase


class Ports(YangBase):
    '''Description from yang model goes here'''
    def __init__(self, parent, yang_key_value=None):
        self.YANG_MODULE = 'openhltest-session'
        self.YANG_CLASS = 'ports'
        super(Ports, self).__init__(parent, yang_key_value)

    @property
    def name(self):
        return getattr(self, 'name')


class Config(YangBase):
    '''Description from yang model goes here'''
    def __init__(self, parent, yang_key_value=None):
        self.YANG_MODULE = 'openhltest-session'
        self.YANG_CLASS = 'config'
        super(Config, self).__init__(parent, yang_key_value)

    @property
    def description(self):
        return self._get_value('description')
    @description.setter
    def description(self):
        self._set_value('description', value)
        
    def ports(self, name=None):
        return Ports(self, name)

    def create_ports(self, name, description=None):
        return self.transport.create_object(locals())


class Statistics(YangBase):
    '''Description from yang model goes here'''
    def __init__(self, parent, yang_key_value=None):
        self.YANG_MODULE = 'openhltest-session'
        self.YANG_CLASS = 'statistics'
        super(Statistics, self).__init__(parent, yang_key_value)

    @property
    def last_activity_timestamp(self):
        return self._get_value('last-activity-timestamp')

    @property
    def first_activity_timestamp(self):
        return self._get_value('first-activity-timestamp')

    def ports(self, name=None):
        return self.transport.get_object(Ports(self, name))
    


class Sessions(YangBase):
    '''Description from yang model goes here'''
    def __init__(self, parent, yang_key_value=None):
        self.YANG_MODULE = 'openhltest-session'
        self.YANG_CLASS = 'sessions'
        super(Sessions, self).__init__(parent, yang_key_value)
    
    @property
    def name(self):
        '''Description from yang model goes here'''
        return self._get_value('name')

    @property
    def session_type(self):
        '''Description from yang model goes here'''
        return self._get_value('session-type')

    def config(self):
        '''Description from yang model goes here'''
        return self.transport.get_object(Config(self))

    def statistics(self):
        '''Description from yang model goes here'''
        return self.transport.get_object(Statistics(self))


class OpenHlTest(YangBase):
    '''Description from yang model goes here'''

    def __init__(self, ip_address, rest_port):
        self.YANG_MODULE = ''
        self.YANG_CLASS = ''
        super(OpenHlTest, self).__init__(HttpTransport(ip_address, rest_port), None)

    def sessions(self, name=None):
        '''Description from yang model goes here'''
        return self.transport.get_object(Sessions(self, name))

    def create_sessions(self, name, session_type='L2L3', description=None):
        '''Create a new sessions object'''
        return self.transport.create_object(self, Sessions(self, name), locals())

    def authenticate(self, username, password):
        '''Description from yang model goes here'''
        payload = {
            'openhltest-session:input': {
                'username': username,
                'password': password
            }
        }
        return self._restconf.post('/restconf/operations/openhltest-session:authenticate', payload)



openhltest = OpenHlTest('127.0.0.1', 443)
#openhltest.authenticate('admin', 'admin')

session = openhltest.create_sessions('demo', description='Vendor prototype demo session')
session.dump()

config = session.config()
config.dump()

statistics = session.statistics()
statistics.dump()

for port in config.ports():
    port.dump()
