import logging

import visa


LOGGER = logging.getLogger(__file__)


ERROR_STATUS = {
    1: 'Unrecognized command/query header',
    2: 'Invalid character',
    3: 'Invalid separator',
    4: 'Missing parameter',
    5: 'Unrecognized keyword',
    6: 'String error',
    7: 'Parameter not allowed',
    8: 'Command string too long',
    9: 'Query not allowed',
    10: 'Missing query mask',
    11: 'Invalid parameter',
    12: 'Parameter syntax error',
    13: 'Too long filename',
}

class Oscilloscope:

    def __init__(self, addr):
        resources = visa.ResourceManager()
        LOGGER.info('Connecting %s.', addr)
        self.connection = resources.open_resource(addr,
                                                  write_termination='\n',
                                                  read_termination='\n')
        self.connection.timeout = 4000

    def write(self, command, block=True):
        self.connection.write(command)
        self._check_for_errors()
        if block:
            self._wait_until_ready()

    def query(self, command):
        response = self.connection.query(command)
        self._check_for_errors()
        return response

    def close(self):
        self.connection.close()

    def _wait_until_ready(self):
        self.connection.write('*OPC?')

    def _check_for_errors(self):
        status = self.connection.query('CMR?')
        error = ERROR_STATUS.get(status)
        if error:
            raise IOError(error)

    def reset(self):
        self.write('*RST')

    def auto_setup(self):
        self.write('AUTO_SETUP')