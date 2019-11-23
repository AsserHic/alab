import logging

import visa


LOGGER = logging.getLogger(__file__)


class Oscilloscope:

    def __init__(self, addr):
        resources = visa.ResourceManager()
        LOGGER.info('Connecting %s.', addr)
        self.connection = resources.open_resource(addr,
                                                  write_termination='\n',
                                                  read_termination='\n')
        self.connection.timeout = 4000

    def write(self, command):
        self.connection.write(command)

    def query(self, command):
        response = self.connection.query(command)
        return response

    def close(self):
        self.connection.close()
