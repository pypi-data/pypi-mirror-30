import argparse
import os

from parosm.parse import *
from parosm.types import *


node_counter = 0
way_counter = 0
relation_counter = 0
osm_obj = None


def parse_args():
    parser = argparse.ArgumentParser(
        description='Read a OSM-XML file and give info'
    )
    parser.add_argument('input',
                        type=str,
                        help='OSM file to read')
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument('--pbf',
                            action='store_true',
                            help='Input file is pbf')
    type_group.add_argument('--xml',
                            action='store_true',
                            help='Input file is xml (default)')
    return parser.parse_args()


def counter(obj):
    global node_counter
    global way_counter
    global relation_counter
    global osm_obj

    if isinstance(obj, Node):
        node_counter += 1
    elif isinstance(obj, Way):
        way_counter += 1
    elif isinstance(obj, Relation):
        relation_counter += 1
    elif isinstance(obj, OSM):
        osm_obj = obj


def main():
    args = parse_args()
    if not os.path.isfile(args.input):
        raise Exception('File does not exist: {}'.format(args.input))
    if args.pbf:
        parser = PBFParser(args.input, counter)
    else:
        parser = XMLParser(args.input, counter)
    parser.parse()
    print('Bounds: N={}, E={}, S={}, W={}'.format(
        osm_obj.bounds['maxlon'],
        osm_obj.bounds['maxlat'],
        osm_obj.bounds['minlon'],
        osm_obj.bounds['minlat'])
    )
    print('Nodes:     {}'.format(node_counter))
    print('Ways:      {}'.format(way_counter))
    print('Relations: {}'.format(relation_counter))


if __name__ == '__main__':
    main()
