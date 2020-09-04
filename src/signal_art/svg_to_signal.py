import argparse
import logging

import numpy
import pandas
from svg.path import parse_path, Path
import xml.etree.ElementTree as ET

from .render_signal import show_xy_graph


LOGGER = logging.getLogger(__file__)


def path_to_df(path: Path):
    LOGGER.info('Processing a path...')
    x = []
    y = []
    for step in path:
        if step.length() == 0:
            next
        for t in numpy.arange(0.0, 1.0, 0.3):
            loc = step.point(t)
            x.append(loc.real)
            y.append(loc.imag)
    df = pandas.DataFrame({
        'x': x,
        'y': y,
    })
    LOGGER.info('Obtained %s data points in total.', df.shape[0])
    df = df.apply(_normalize, axis=0)
    df.y = 1 - df.y
    return df


def _normalize(series):
    low = series.min()
    high = series.max()
    return (series - low) / (high - low)


def _to_csv(data: pandas.DataFrame, filename: str):
    LOGGER.info('Writing %s.', filename)
    data.to_csv(filename, sep='\t')


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

    file_prefix = filename.split('.')[0]
    _to_csv(df['x'], f"{file_prefix}_x.csv")
    _to_csv(df['y'], f"{file_prefix}_y.csv")
