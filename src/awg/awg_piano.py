import argparse
import keyboard
import logging
import sys
import time

from awg import SignalGenerator

LOGGER = logging.getLogger(__file__)

NOTE_OFFSET = {
    'c': -9,
    'c#': -8,
    'd': -7,
    'd#': -6,
    'e': -5,
    'f': -4,
    'f#': -3,
    'g': -2,
    'g#': -1,
    'a': 0,
    'a#': 1,
    'b': 2,
}

NOTE_KEYS = {
    'a': 'c',
    'w': 'c#',
    's': 'd',
    'e': 'd#',
    'd': 'e',
    'f': 'f',
    'r': 'f#',
    'g': 'g',
    't': 'g#',
    'h': 'a',
    'y': 'a#',
    'j': 'b',
}

WAVE_FORMS = [
    'SINE',
    'SQUARE',
    'RAMP',
    'ARB 2',  # StairUD
    'ARB 5',  # Trapezia
    'ARB 14',  # X^2
    'ARB 16',  # Sinc
    'ARB 17',  # Gaussian
    'ARB 18',  # Dlorentz
    'ARB 21',  # Gauspuls
    'ARB 22',  # Gmonopuls
    'ARB 24',  # Cardiac
    'ARB 26',  # Chirp
    'ARB 27',  # TwoTone
    'ARB 28',  # SNR
]


class Piano:

    def __init__(self, addr):
        self._awg = SignalGenerator(addr)
        self._awg.write("C1:BASIC_WAVE AMP,0.9")
        self._awg.set_output(1, True)
        self._octave = 4
        self._wave_index = 0

    def next_wave(self, direction: bool = True):
        incr = 1 if direction else -1
        self._wave_index = (self._wave_index + incr) % len(WAVE_FORMS)
        self._awg.set_waveform(1, WAVE_FORMS[self._wave_index])

    @property
    def octave(self):
        return self._octave

    @octave.setter
    def octave(self, value: int):
        if value < 0 or value > 9:
            raise ValueError(f"Invalid octave: {value}.")
        if value != self._octave:
            self._octave = value
            LOGGER.info('Select octave %s.', value)

    def close(self):
        self._awg.close()
        self._awg = None

    def is_alive(self):
        return self._awg is not None

    def play_note(self, note: str):
        if note is None:
            return
        freq = self.note_frequency(note, self._octave)
        LOGGER.info('Play %s%s (%s Hz).', note, self._octave, freq)
        self._awg.set_frequency(freq, 1)

    @staticmethod
    def note_frequency(note, octave):
        n = NOTE_OFFSET[note] + (octave - 4) * 12
        return round(440 * 1.059463094359 ** n, 2)


def _set_octave(piano, key):
    try:
        piano.octave = int(key)
    except ValueError:
        LOGGER.warning("Invalid octave: %s.", key)


def _stop(piano):
    piano.close()
    keyboard.send('enter')


def run(args: argparse.Namespace):
    piano = Piano(args.config['awg'].get('address'))

    for key in NOTE_KEYS:
        keyboard.on_press_key(key, lambda event: piano.play_note(NOTE_KEYS.get(event.name)), suppress=True)

    for key in range(0, 10):
        keyboard.on_press_key(str(key), lambda event: _set_octave(piano, event.name), suppress=True)

    keyboard.on_press_key('c', lambda event: _stop(piano), suppress=True)
    keyboard.on_press_key('n', lambda event: piano.next_wave(False), suppress=True)
    keyboard.on_press_key('m', lambda event: piano.next_wave(True), suppress=True)

    LOGGER.info('Ready!')
    while piano.is_alive():
        time.sleep(1)
        sys.stdin.readline()  # Clear buffer
    LOGGER.info('Bye!')
