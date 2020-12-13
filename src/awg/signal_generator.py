import logging

import visa

LOGGER = logging.getLogger(__file__)


class SignalGenerator:

    def __init__(self, addr):
        if addr:
            LOGGER.info('Connecting %s.', addr)
            resources = visa.ResourceManager()
            self._connection = resources.open_resource(addr, timeout=50000, chunk_size = 24*1024*1024)
        else:
            LOGGER.info('Signal generator in dry-run mode!')
            self._connection = None

        self._frequency = [-1.0, -1.0]

    def write(self, command):
        if self._connection:
            self._connection.write(command)
        else:
            LOGGER.info("WRITE: %s", command)

    def write_raw(self, command):
        if self._connection:
            term_sign = self._connection.write_termination
            self._connection.write_termination = ''
            self._connection.write(command, encoding='latin1')
            self._connection.write_termination = term_sign
        else:
            LOGGER.info("WRITE <binary>")

    def query(self, command):
        response = self._connection.query(command)
        return response

    def identify(self):
        return self.query('*IDN?')

    def reset(self):
        self.write('*RST')

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
    if channel != 1 and channel != 2:
        raise ValueError(f"Invalid channel: {channel}.")
