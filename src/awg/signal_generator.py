import logging

import visa


LOGGER = logging.getLogger(__file__)


class SignalGenerator:

    def __init__(self, addr):
        resources = visa.ResourceManager()
        LOGGER.info('Connecting %s.', addr)
        self.connection = resources.open_resource(addr,
                                                  write_termination='\n',
                                                  read_termination='\x00\n')
        self.connection.timeout = 4000
        self.connection.query_delay = 1.0

        LOGGER.info('Connected to %s.', self.query('*IDN?'))

    def write(self, command):
        self.connection.write(command)

    def query(self, command):
        response = self.connection.query(command)
        return response

    def close(self):
        self.connection.close()