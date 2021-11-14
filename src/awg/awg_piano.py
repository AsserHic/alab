import argparse
import logging
import random
import sys
import time
from typing import List, Optional  # noqa: F401

import keyboard

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

    def __init__(self, addr, a4_hz: float = 440, amplitude: float = 0.9):
        self._awg = SignalGenerator(addr)
        self._awg.reset()
        time.sleep(2)
        for channel in [1, 2]:
            self._awg.write(f"C{channel}:BASIC_WAVE AMP,{amplitude},FRQ,0HZ")
            self._awg.set_output(channel, True)
        self._octave = 4
        self._wave_index = 0
        self._harmonics = False
        self._amplitude = amplitude
        self._channels = [None, None]  # type: List[Optional[str]]
        self._a4 = a4_hz

    def next_wave(self, direction: bool = True):
        incr = 1 if direction else -1
        self._update_waveform((self._wave_index + incr) % len(WAVE_FORMS))

    def _update_waveform(self, index: int):
        if self._harmonics:
            for channel in [1, 2]:
                self._awg.write(f'C{channel}:HARM HARMSTATE,OFF')
            self._harmonics = False
        self._wave_index = index
        for channel in [1, 2]:
            self._awg.set_waveform(channel, WAVE_FORMS[self._wave_index])

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

    def _get_channel(self, note: str):
        channel = 0
        for chn, note_active in enumerate(self._channels):
            if note_active == note:
                return chn + 1
            if note_active is None:
                channel = chn
        return channel + 1

    def play_note(self, note: Optional[str]):
        if note is None:
            return
        freq = self.note_frequency(note, self._octave)
        channel = self._get_channel(note)
        if freq != self._awg.get_frequency(channel):
            LOGGER.info('Play %s%s (%s Hz) on channel %s.',
                        note, self._octave, freq, channel)
            self._channels[channel - 1] = note
            self._awg.set_frequency(freq, channel)

    def release_note(self, note: Optional[str]):
        if note is None:
            return
        channel = self._get_channel(note)
        # LOGGER.info('Release channel %s.', channel)
        self._channels[channel - 1] = None
        self._awg.set_frequency(0, channel)

    def note_frequency(self, note, octave):
        n = NOTE_OFFSET[note] + (octave - 4) * 12
        return round(self._a4 * 1.059463094359 ** n, 2)

    def random_harmonics(self):
        if not self._harmonics:
            self._update_waveform(0)
            for channel in [1, 2]:
                self._awg.write(f'C{channel}:HARM HARMSTATE,ON,HARMTYPE,ALL')
            self._harmonics = True
            time.sleep(2)
        LOGGER.info('Generating randomized harmonics...')
        order = random.randrange(2, 15)
        if random.uniform(0, 1) < 0.7:
            amp = random.uniform(0, self._amplitude * 0.8)
            phase = random.randrange(0, 180)
        else:
            amp = 0
            phase = 0
        LOGGER.info('   order %s: %s', order, 'muted' if amp < 0.001 else f'set {amp:.2f} Vpp {phase} degree')
        for channel in [1, 2]:
            self._awg.write(f'C{channel}:HARM HARMORDER,{order},HARMAMP,{amp:.2f},HARMPHASE,{phase}')
            time.sleep(1)
        LOGGER.info('   done!')


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
        keyboard.on_release_key(key, lambda event: piano.release_note(NOTE_KEYS.get(event.name)), suppress=True)

    for key in map(str, range(0, 10)):
        keyboard.on_press_key(key, lambda event: _set_octave(piano, event.name), suppress=True)

    keyboard.on_press_key('b', lambda event: piano.random_harmonics(), suppress=True)
    keyboard.on_press_key('c', lambda event: _stop(piano), suppress=True)
    keyboard.on_press_key('n', lambda event: piano.next_wave(False), suppress=True)
    keyboard.on_press_key('m', lambda event: piano.next_wave(True), suppress=True)

    LOGGER.info('Keys: c = exit, b = harmonics, n,m = select waveform, 0-9 = octave')
    LOGGER.info(", ".join([f"{key}={note}" for key, note in NOTE_KEYS.items()]))

    while piano.is_alive():
        time.sleep(1)
        sys.stdin.readline()  # Clear buffer
    LOGGER.info('Bye!')
