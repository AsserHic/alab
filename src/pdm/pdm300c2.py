import serial


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
        value = self._con.read()
        return value

    def close(self):
        self._con.close()
