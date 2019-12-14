import logging
import time

import visa
import wave


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
        resources = visa.ResourceManager('@py')
        LOGGER.info('Connecting %s.', addr)
        self.connection = resources.open_resource(addr,
                                                  write_termination='\n',
                                                  read_termination='\n')
        self.connection.timeout = 5000
        self.connection.query_delay = 1

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
        LOGGER.info('Connection closed for: %s', self.addr)

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

    def sample_rate(self, channel):
        rate = self.query(f"SAMPLE_RATE? C{channel}")
        rate = int(float(rate[5:-6]))
        return rate

    def save_measures(self, channel, filename):
        rate = self.sample_rate(channel)
        LOGGER.info('Sample rate is %s.', rate)

        self.write('WAVEFORM_SETUP SP,4,NP,100,FP,0')
        print(self.connection.query('TEMPLATE?'))
        self.connection.write(f"C{channel}: WAVEFORM? DAT2")
        #response = self.connection.read_bytes(1000, break_on_termchar='\0')
        response = self.connection.read_raw()
        #response = self.query("C1: WF? ALL")

        print(response)
        if not response.startswith(f"C{channel}: WF ALL"):
            raise ValueError(f'Unexpected oscilloscope output: {response[:80]}')

        index = response.index('#9')
        index_start_data = index + 2 + 9
        data_size = int(response[index + 2:index_start_data])
        print(data_size)
        data = response[index_start_data:index_start_data + data_size]
        print(len(data))

        wave_out = wave.open(filename, 'w')
        wave_out.setparams((
            1,               # nchannels
            1,               # sampwidth
            sample_rate,     # framerate
            data_size,       # nframes
            "NONE",          # comptype
            "not compresse", # compname
        ))
        wave_out.writeframes(data)
        wave_out.close()