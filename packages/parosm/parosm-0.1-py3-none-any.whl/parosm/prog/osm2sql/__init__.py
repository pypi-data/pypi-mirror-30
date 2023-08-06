import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Read a OSM-XML file and put out a SQL Query'
    )
    parser.add_argument('input',
                        type=str,
                        help='OSM file to read')
    parser.add_argument('output',
                        type=str,
                        help='Output path or "-" for stdout')
    return parser.parse_args()


def main():
    args = parse_args()
    print(args.input)
    print(args.output)


if __name__ == '__main__':
    main()
