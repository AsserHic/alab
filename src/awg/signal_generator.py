import logging

import visa

LOGGER = logging.getLogger(__file__)


class SignalGenerator:

    def __init__(self, addr):
        if addr:
            LOGGER.info('Connecting %s.', addr)
            resources = visa.ResourceManager()
            self._connection = resources.open_resource(addr,
                                                       chunk_size=40 * 1024,
                                                       write_termination='\n',
                                                       read_termination='\n')
            self._connection.timeout = 5000
            self._connection.query_delay = 1.0
        else:
            LOGGER.info('Signal generator in dry-run mode!')
            self._connection = None

        self._frequency = [-1.0, -1.0]

    def write(self, command):
        if self._connection:
            self._connection.write(command)
        else:
            LOGGER.info("WRITE: %s", command)

    def query(self, command):
        response = self._connection.query(command)
        return response

    def set_amplitude(self, channel, volts: float):
        _validate_channel(channel)
        self.write(f"C{channel}:BASIC_WAVE AMP,{volts}")

    def set_offset(self, channel, volts: float):
        _validate_channel(channel)
        self.write(f"C{channel}:BASIC_WAVE OFST,{round(volts, 3)}")

    def set_output(self, channel, status):
        _validate_channel(channel)
        self.write(f"C{channel}:OUTPUT {'ON' if status else 'OFF'}")

    def set_waveform(self, channel, waveform: str):
        _validate_channel(channel)
        LOGGER.info('Waveform selection: %s.', waveform)
        if waveform.startswith('ARB '):
            self.write(f"C{channel}:ARWV INDEX,{waveform[4:]}")
            waveform = 'ARB'
        self.write(f"C{channel}:BASIC_WAVE WVTP,{waveform}")

    def get_frequency(self, channel):
        return self._frequency[channel - 1]

    def set_frequency(self, freq, channel):
        if self._frequency[channel - 1] == freq:
            return
        self._frequency[channel - 1] = freq
        self.write(f"C{channel}:BASIC_WAVE FRQ,{freq}")

    def close(self):
        if self._connection:
            self.set_output(1, False)
            self.set_output(2, False)
            self._connection.close()


def _validate_channel(channel: int):
    if channel is not 1 and \
       channel is not 2:
        raise ValueError(f"Invalid channel: {channel}.")
