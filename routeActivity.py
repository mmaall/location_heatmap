import folium
from folium.plugins import HeatMap
import logging 
import sys
import argparse
import os 
from FileHandler import GpsDataFile

def main(argv):

    # Deal with the arguments  
    p = argparse.ArgumentParser()

    p.add_argument("path", help= "Path to valid gps file")

    p.add_argument(
            '-d', '--directory',
            help='Process a directory rather than a single file',
            action= 'store_true'
        )

    p.add_argument(
            '-D', '--debug',
            help='Enable debug mode',
            action= 'store_true'
        )

    p.add_argument(
            "-s", "--sampling_factor", 
            help= "input a sampling factor between [0 and 1)",
            type= float,
        )

    args = p.parse_args()
    
    if args.debug:
        logging.basicConfig(level= logging.DEBUG)

    samplingFactor = 1

    # Verify correctness of sampling factor
    if args.sampling_factor:
        sampling_factor = args.sampling_factor
        try:
            sampling_factor= float(sampling_factor)
        except ValueError as e:
            print("Sampling factor must be an integer or float")
            print(str(e))
            exit()
        samplingFactor = sampling_factor

    logging.debug("Sampling factor: {}".format(samplingFactor))
    # Holds the valid file extensions we can handle.
    # This may need to be extracted into a config file to be pretty
    validExtensions = [".gpx", ".fit"]

    # define the path 
    path = args.path
    # initialize list to hold file names 

    fileName = ""    


    # Reject a directory
    if os.path.isdir(path):
        print("Must use a file not a directory")
        exit()
    else:
        fileName = path
    
    # loop through all the files and append their coordinates to a giant coordinate list 
    logging.debug("Extracting from {}".format(fileName))
    try:
        gpsFile = GpsDataFile(fileName, samplingFactor= samplingFactor)
    except Exception as e:
        logging.debug("Error thrown while parsing {}. ".format(fileName))
        logging.debug(str(e))
        logging.debug("File ignored, processing continues") 

    m = folium.Map(
            location= gpsFile.getCenter(), 
            zoom_start = 12,
            tiles = "Stamen Terrain" 
        )

    folium.map.Marker(gpsFile.getFirstCoordinate(), popup = "Start").add_to(m)
    folium.map.Marker(gpsFile.getLastCoordinate(), popup = "Finish").add_to(m)

    folium.vector_layers.PolyLine(gpsFile.getCoordinateList()).add_to(m)



    m.save("index.html") 
    # okay so now what we need to do is figure out how the fuck this heatmap stuff works


if __name__ == "__main__":
    main(sys.argv[1:])
