import argparse
import logging
import xml.etree.ElementTree as ET

import numpy
import pandas
from svg.path import parse_path, Path

from .render_signal import show_xy_graph


LOGGER = logging.getLogger(__file__)


def path_to_df(path: Path) -> pandas.DataFrame:
    LOGGER.info('Processing a path...')
    x = []
    y = []
    for step in path:
        if step.length() == 0:
            continue
        for phase in numpy.arange(0.0, 1.0, 0.3):
            loc = step.point(phase)
            x.append(loc.real)
            y.append(loc.imag)
    data = pandas.DataFrame({
        'x': x,
        'y': y,
    })
    data = data.apply(_normalize, axis=0)
    data.y = 1 - data.y
    data.drop_duplicates(inplace=True)
    LOGGER.info('Obtained %s data points in total.', data.shape[0])
    return data


def _normalize(series):
    low = series.min()
    high = series.max()
    return (series - low) / (high - low)


def _to_csv(data: pandas.Series, filename: str) -> None:
    LOGGER.info('Writing %s.', filename)
    step = 0.00000001
    data = pandas.DataFrame({
        'Second': numpy.arange(0.0, step * len(data), step)[:len(data)],
        'Volt': data,
    })
    data.to_csv(filename, index=False)


def populate_cli_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--file',
                        default='drawing.svg',
                        type=str,
                        help='Name of the input SVG file')


def run(args: argparse.Namespace):
    xml = ET.parse(args.file)
    root = xml.getroot()
    data = None  # type: pandas.DataFrame
    for item in root.iter('{http://www.w3.org/2000/svg}path'):
        if data is not None:
            LOGGER.warning("%s contains more than one path! Using the first one.",
                           args.file)
            break
        data = path_to_df(parse_path(item.attrib['d']))

    if not args.dry:
        LOGGER.info('Rendering XY-graph to the display.')
        show_xy_graph(data)

    file_prefix = args.file.split('.')[0]
    _to_csv(data['x'], f"{file_prefix}_x.csv")
    _to_csv(data['y'], f"{file_prefix}_y.csv")
