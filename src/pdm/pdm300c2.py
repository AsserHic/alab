# Parkside digital multimeter PDM 300 C2
#
# Special thanks for: https://github.com/benedikts-workshop/ParksideView
# and https://www.mikrocontroller.net/articles/Multimeter_PDM-300-C2_Analyse

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
    int('10000000', 2): ('H',    {}),
}


class PDM300:

    def __init__(self, port):
        self._con = serial.Serial(
            port=port,
            baudrate=2400,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)

    def read(self):
        self._synchronize()
        msg = self._con.read(8)
        if not _checksum(msg):
            return {'error': 'Checksum mismatch'}
        mode = MODES[msg[MSG_MODE]]
        response = {'mode': mode[LABEL]}
        if not mode[UNIT]:
            return response

        rng = RANGES[msg[MSG_RANGE]]
        response['range'] = rng[LABEL]

        raw = _as_int(msg[MSG_VALUE1], msg[MSG_VALUE2])
        response['raw'] = raw

        denominator = rng[FRACTION].get(mode[LABEL])
        if not denominator:
            return response
        response['value'] = raw / denominator
        response['unit'] = mode[UNIT]
        return response

    def close(self):
        self._con.close()

    def _synchronize(self):
        for trial in range(1, 20):
            byte = self._con.read()
            if byte == b'\xdc' and self._con.read() == b'\xba':
                return
        raise IOError("Cannot synchronize with the PDM 300 C2 UART.")


def _as_int(byte1, byte2):
    return byte1 << 8 | byte2


def _checksum(msg):
    csum = msg[0]+msg[1]+msg[2]+msg[3]+msg[4]+msg[5]
    expected = _as_int(msg[MSG_CHECK1], msg[MSG_CHECK2])
    return csum == expected
