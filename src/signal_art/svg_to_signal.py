import argparse
import logging

from svg.path import parse_path, Path
import xml.etree.ElementTree as ET

LOGGER = logging.getLogger(__file__)


def path_to_df(path: Path):
    for step in path:
        start = step.point(0)
        x = start.real
        y = start.imag
        print(f"{x}, {y}")

def run(args: argparse.Namespace):
    filename = '../drawing.svg'

    xml = ET.parse(filename)
    root = xml.getroot()
    for item in root.iter('{http://www.w3.org/2000/svg}path'):
        path_to_df(parse_path(item.attrib['d']))
