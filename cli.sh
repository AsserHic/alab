#!/bin/bash

set -e

export PYTHONPATH=src
python3 -m cli $@
