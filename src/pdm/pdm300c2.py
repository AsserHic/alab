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
        self._synchronize()
        msg = self._con.read(8)
        if not _checksum(msg):
            return {}
        return msg

    def close(self):
        self._con.close()

    def _synchronize(self):
        for trial in range(1, 20):
            byte = self._con.read()
            if byte == b'\xdc' and self._con.read() == b'\xba':
                return
        raise IOError("Cannot synchronize with the PDM 300 C2 UART.")

def _checksum(msg):
    csum = msg[0]+msg[1]+msg[2]+msg[3]+msg[4]+msg[5]+msg[6]
    return csum - msg[7] == 0
