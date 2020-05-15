# Parkside digital multimeter PDM 300 C2
#
# Special thanks for: https://github.com/benedikts-workshop/ParksideView
# and https://www.mikrocontroller.net/articles/Multimeter_PDM-300-C2_Analyse

import logging
import serial

MSG_MODE = 1
MSG_RANGE = 2
MSG_VALUE1 = 4
MSG_VALUE2 = 5
MSG_CHECK1 = 6
MSG_CHECK2 = 7

FRACTION = 1
LABEL = 0
UNIT = 1

MODES = {
    int('00010110', 2): ('DC',         'V'),
    int('00010101', 2): ('AC',         'V'),
    int('00011101', 2): ('resistance', 'Ohm'),
    int('00011011', 2): ('continuity', 'Ohm'),
    int('00011100', 2): ('diode',      'V'),
    int('00000011', 2): ('squarewave', None),
    int('00011010', 2): ('uA',         'A'),
    int('00011001', 2): ('mA',         'A'),
    int('00011000', 2): ('A',          'A'),
}

RANGES = {
    int('00000000', 2): ('init', {}),
    int('00000001', 2): ('A',    {'resistance': 10,
                                  'continuity': 10}),
    int('00000010', 2): ('B',    {'DC':         10000,
                                  'resistance': 1,
                                  'uA':         10000000}),
    int('00000100', 2): ('C',    {'DC':         1000,
                                  'AC':         1000,
                                  'resistance': 0.1,
                                  'diode':      1000,
                                  'uA':         1000000}),
    int('00001000', 2): ('D',    {'DC':         100,
                                  'AC':         100,
                                  'resistance': 0.01,
                                  'mA':         1000}),
    int('00010000', 2): ('E',    {'DC':         10,
                                  'AC':         10,
                                  'resistance': 0.001,
                                  'mA':         100}),
    int('00100000', 2): ('F',    {'DC':         1,
                                  'AC':         1,
                                  'resistance': 0.0001,
                                  'A':          1000}),
    int('01000000', 2): ('G',    {'A':          100}),
}

LOGGER = logging.getLogger(__file__)


class PDM300:

    def __init__(self, port):
        if port:
            LOGGER.info("Connecting a multimeter at %s...", port)
            self._con = serial.Serial(
                port=port,
                baudrate=2400,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1)
        else:
            LOGGER.info("Running multimeter in dry mode.")
            self._con = None

    def read(self):
        if not self._con:
            return {'error': 'disconnected'}

        self._synchronize()
        msg = self._con.read(8)
        if not self._checksum(msg):
            return {'error': 'Checksum mismatch'}
        mode = MODES.get(msg[MSG_MODE])
        if not mode:
            return {'error': f'unexpected mode: {msg[MSG_MODE]}'}
        response = {'mode': mode[LABEL]}
        if not mode[UNIT]:
            return response

        rng = RANGES[msg[MSG_RANGE]]
        response['range'] = rng[LABEL]

        raw = int.from_bytes(msg[MSG_VALUE1:MSG_VALUE2+1], byteorder='big', signed=True)
        response['raw'] = raw
        if _is_overflow(raw, mode, rng):
            response['error'] = 'overflow'
            return response

        denominator = rng[FRACTION].get(mode[LABEL])
        if not denominator:
            return response
        response['value'] = raw / denominator
        response['unit'] = mode[UNIT]
        return response

    def close(self):
        if self._con:
            self._con.close()
            self._con = None

    def _synchronize(self):
        for trial in range(1, 20):
            byte = self._con.read()
            if byte == b'\xdc' and self._con.read() == b'\xba':
                return
        raise IOError("Cannot synchronize with the PDM 300 C2 UART.")

    def _checksum(self, msg) -> bool:
        if len(msg) < 8:
            self.close()
            return False

        csum = msg[0]+msg[1]+msg[2]+msg[3]+msg[4]+msg[5]
        expected = msg[MSG_CHECK1] << 8 | msg[MSG_CHECK2]
        return csum == expected


def _is_overflow(value, mode, rng):
    dist = abs(value)
    return (dist > 1999) or \
           (mode[LABEL] == 'DC' and rng[LABEL] == 'F' and dist > 300) or \
           (mode[LABEL] == 'A' and rng[LABEL] == 'G' and dist > 1000) or \
           (mode[LABEL] == 'resistance' and value < 0) or \
           (mode[LABEL] == 'continuity' and rng[LABEL] == 'C')
