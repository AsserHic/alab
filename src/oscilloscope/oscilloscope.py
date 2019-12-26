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
        self.addr = addr
        if addr:
            resources = visa.ResourceManager('@py')
            LOGGER.info('Connecting %s.', addr)
            self._connection = resources.open_resource(addr,
                                                       write_termination='\n',
                                                       read_termination='\n')
            self._connection.timeout = 5000
            self._connection.query_delay = 1
        else:
            LOGGER.info('Oscilloscope in dry-run mode!')
            self._connection = None

    def write(self, command, block=True):
        if self._connection:
            self._connection.write(command)
            self._check_for_errors()
            if block:
                self._wait_until_ready()
        else:
            LOGGER.info("WRITE: %s", command)

    def query(self, command):
        response = self._connection.query(command)
        self._check_for_errors()
        return response

    def close(self):
        if self._connection:
            self._connection.close()
            LOGGER.info('Connection closed for: %s', self.addr)

    def _wait_until_ready(self):
        self._connection.write('*OPC?')

    def _check_for_errors(self):
        status = self._connection.query('CMR?')
        error = ERROR_STATUS.get(status)
        if error:
            raise IOError(error)

    def reset(self):
        self.write('*RST')

    def auto_setup(self):
        self.write('AUTO_SETUP')

    def sample_rate(self, channel):
        rate = self.query(f"SAMPLE_RATE? C{channel}")
        rate = int(float(rate[5:-6]))
        return rate
