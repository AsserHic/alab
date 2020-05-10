import serial

MSG_MODE = 1
MSG_RANGE = 2
MSG_VALUE1 = 4
MSG_VALUE2 = 5
MSG_CHECK1 = 6
MSG_CHECK2 = 7

LABEL = 0
UNIT = 1

MODES = {
    int('00010110', 2): ('DC V',       'V'),
    int('00010101', 2): ('AC V',       'V'),
    int('00011010', 2): ('uA',         'A'),
    int('00011001', 2): ('mA',         'A'),
    int('00011000', 2): ('A',          'A'),
    int('00011100', 2): ('diode',      'Ohm'),
    int('00011011', 2): ('continuity', 'Ohm'),
    int('00000011', 2): ('squarewave', None),
    int('00011101', 2): ('resistance', 'Ohm'),
}

RANGES = {
    int('00000000', 2): ('init', ),
    int('00000001', 2): ('A', ),
    int('00000010', 2): ('B', ),
    int('00000100', 2): ('C', ),
    int('00001000', 2): ('D', ),
    int('00010000', 2): ('E', ),
    int('00100000', 2): ('F', ),
    int('01000000', 2): ('G', ),
    int('10000000', 2): ('H', ),
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
        rng = RANGES[msg[MSG_RANGE]]

        if not mode[UNIT]:
            return {'mode': mode[LABEL]}

        value = _as_int(msg[MSG_VALUE1], msg[MSG_VALUE2])

        response = {
            'mode': mode[LABEL],
            'range': rng[LABEL],
            'unit': mode[UNIT],
            'value': value,
        }
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
