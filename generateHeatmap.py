import folium
import logging 
import sys
import argparse
from FileHandler import GpsData

def main(argv):
    p = argparse.ArgumentParser()

    p.add_argument("path", help= "Path to valid gps files")

    p.add_argument(
            '-d', '--debug',
            help='Enable debug mode',
            action= 'store_true'
        )


    args = p.parse_args()
    if args.debug:
        logging.basicConfig(level= logging.DEBUG)


if __name__ == "__main__":
    main(sys.argv[1:])