Asser's laboratory
==================

This repository contains miscellanous command line applications and demonstrations
for the laboratory equipment.

You can find more information about these programs and the equipment from my YouTube channel:
[Asser's Lab](https://www.youtube.com/channel/UCN_t7E-0wGlAN78wcCkMscw).

Equipment
---------

The codes are executed on a Raspberry Pi 4.

The arbitrary waveform generator (***awg***) is Siglent SDG 1032X.
I have controlled it with SCPI via USB.

The ***oscilloscope*** is Siglent SDS 1104X-E.
I have controlled it with SCPI via USB.

The ***pdm*** multimeter stands for Parkside PDM 300 C2, which I modified so that its serial output (TX)
is exposed to the controlling Raspberry Pi.
I am reading the multimeter with the custom code that you can find from this library.

Usage
-----

Device configurations can be found from `src/alab_config.ini`.

All routines are mapped to `./cli.sh` script and you can use its arguments to lauch them.
