import logging

import visa

LOGGER = logging.getLogger(__file__)


class SignalGenerator:

    def __init__(self, addr):
        if addr:
            LOGGER.info('Connecting %s.', addr)
            resources = visa.ResourceManager()
            self._connection = resources.open_resource(addr,
                                                       write_termination='\n',
                                                       read_termination='\x00\n')
            self._connection.timeout = 4000
            self._connection.query_delay = 1.0
            LOGGER.info('Connected to %s.', self.query('*IDN?'))
        else:
            LOGGER.info('Signal generator in dry-run mode!')
            self._connection = None

        self._frequency = -1.0

    def write(self, command):
        if self._connection:
            self._connection.write(command)
        else:
            LOGGER.info("WRITE: %s", command)

    def query(self, command):
        response = self._connection.query(command)
        return response

    def set_output(self, channel, status):
        _validate_channel(channel)
        self.write(f"C{channel}:OUTPUT {'ON' if status else 'OFF'}")

    def set_waveform(self, channel, waveform: str):
        LOGGER.info('Waveform selection: %s.', waveform)
        if waveform.startswith('ARB '):
            cmd = f"C{channel}:ARWV INDEX,{waveform[4:]} ;BASIC_WAVE WVTP,ARB"
        else:
            cmd = f"C{channel}:BASIC_WAVE WVTP,{waveform}"
        self.write(cmd)


    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, freq):
        if self._frequency == freq:
            return
        self._frequency = freq
        self.write(f"C1:BASIC_WAVE FRQ,{freq}")

    def close(self):
        if self._connection:
            self.set_output(1, False)
            self.set_output(2, False)
            self._connection.close()


def _validate_channel(channel: int):
    if channel is not 1 and \
       channel is not 2:
        raise ValueError(f"Invalid channel: {channel}.")
