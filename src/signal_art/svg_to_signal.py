import argparse
import logging

import pandas
from svg.path import parse_path, Path
import xml.etree.ElementTree as ET

from .render_signal import show_xy_graph


LOGGER = logging.getLogger(__file__)


def path_to_df(path: Path):
    x = []
    y = []
    for step in path:
        start = step.point(0)
        x.append(start.real)
        y.append(start.imag)
    df = pandas.DataFrame({
        'x': x,
        'y': y,
    })
    return df


def run(args: argparse.Namespace):
    filename = 'drawing.svg'

    xml = ET.parse(filename)
    root = xml.getroot()
    df = None
    for item in root.iter('{http://www.w3.org/2000/svg}path'):
        if df:
            LOGGER.warn("%s contains more than one path! Using the first one.",
                        filename)
            break
        df = path_to_df(parse_path(item.attrib['d']))
    show_xy_graph(df)
