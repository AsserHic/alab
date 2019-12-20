import argparse
import keyboard
import logging
import time

from awg.signal_generator import SignalGenerator

LOGGER = logging.getLogger(__file__)

NOTE_OFFSET = {
    'c': -9,
    'd': -7,
    'e': -5,
    'f': -4,
    'g': -2,
    'g#': -1,
    'a': 0,
    'a#': 1,
    'b': 2,
}
NOTE_KEYS = {
    'a': 'c',
    's': 'd',
    'd': 'e',
    'f': 'f',
    'g': 'g',
    'h': 'a',
    'j': 'b',
}


class Piano:

    def __init__(self, addr):
        self._awg = SignalGenerator(addr)
        self._awg.write("C1:BASIC_WAVE AMP,0.9")
        self._octave = 4

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

    def play_note(self, note: str):
        if note is None:
            return
        freq = self.note_frequency(note, self._octave)
        LOGGER.info('Play %s%s (%s Hz).', note, self._octave, freq)
        self._awg.frequency = freq

    @staticmethod
    def note_frequency(note, octave):
        n = NOTE_OFFSET[note] + (octave - 4) * 12
        return round(440 * 1.059463094359 ** n, 2)


def _set_octave(piano, key):
    piano.octave = int(key)


def run(args: argparse.Namespace):
    addr = None if args.dry else 'USB0::62700::4355::SDG1XCAQ3R3321::0::INSTR'
    piano = Piano(addr)

    for key in NOTE_KEYS:
        keyboard.on_press_key(key, lambda event: piano.play_note(NOTE_KEYS.get(event.name)), suppress=True)

    for key in range(0, 9):
        keyboard.on_press_key(str(key), lambda event: _set_octave(piano, event.name), suppress=True)

    while True:
        time.sleep(1)

    piano.close()
