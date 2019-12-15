import keyboard
import logging
import time

from awg.signal_generator import SignalGenerator

LOGGER = logging.getLogger(__file__)

NOTES = {
    'c4': 261.63,
    'd4': 293.66,
    'e4': 329.63,
    'f4': 349.23,
    'g4': 392.00,
    'a4': 440.00,
    'b4': 493.88,
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
        self._frequency = 0

    @property
    def octave(self):
        return self._octave

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, freq):
        if self._frequency == freq:
            return
        self._frequency = freq
        self._awg.write(f"C1:BASIC_WAVE FRQ,{freq}")

    def close(self):
        self._awg.close()


def _note_pressed(piano, event):
    octave = piano.octave
    note_full = f"{NOTE_KEYS[event.name]}{octave}"
    freq = NOTES[note_full]
    LOGGER.info('Play %s (%s Hz).', note_full, freq)
    piano.frequency = freq


def run():
    piano = Piano('USB0::62700::4355::SDG1XCAQ3R3321::0::INSTR')

    for key in NOTE_KEYS:
        keyboard.on_press_key(key, lambda event: _note_pressed(piano, event), suppress=True)

    while True:
        time.sleep(1)

    piano.close()
