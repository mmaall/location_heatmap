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

    p.add_argument("path", help= "Path to valid gps files")

    p.add_argument(
            '-d', '--debug',
            help='Enable debug mode',
            action= 'store_true'
        )

    args = p.parse_args()
    if args.debug:
        logging.basicConfig(level= logging.DEBUG)

    # Holds the valid file extensions we can handle.
    # This may need to be extracted into a config file to be pretty
    validExtensions = [".gpx", ".fit"]

    # define the path 
    path = args.path
    # initialize list to hold file names 
    fileNames = []
    

    # Check whether we were given a directory or a file 
    if os.path.isdir(path):
        # If the directory doesn't finish with a backlash we must add one to access the data 
        if path[len(path)-1] != "/":
            path += "/"
        # If we found a directory let's iterate through everything
        logging.debug("Directory given({})".format(path))
        # Get the contents of the directory
        directoryContents = os.listdir(path)
        logging.debug("Directory contents: {}".format(len(directoryContents)))
        # Iterate through them all 
        for fileName in directoryContents:
            # check whether we ran into a file or not
            logging.debug("Path: {}".format(fileName))
            if not os.path.isdir(fileName):
                # verify we have a valid file extension
                strippedFileName, extension = os.path.splitext(fileName)
                # If we have a valid file extension we add it to the files to be parsed 
                if extension in validExtensions:
                    fileNames.append(path+fileName)
                else:
                    logging.debug("Extension {} not supported, {} ignored".format(extension, fileName)) 

    else:
        fileNames.append(path)

    logging.debug("Number of files to parse: {}".format(len(fileNames)))

    coordinateList = []
    # loop through all the files and append their coordinates to a giant coordinate list 
    for file in fileNames:
        logging.debug("Extracting from {}".format(file))
        try:
            data = GpsDataFile(file)
        except Exception as e:
            logging.error("Error thrown while parsing {}. ".format(file))
            logging.error(str(e))
            logging.error("File ignored, processing continues") 
            continue
        coordinateList.extend(data.getCoordinates())


    print(len(coordinateList))

    m = folium.Map(location= [45.5236, -122.6750])


    heatmap = HeatMap(coordinateList, radius = 10)
    
    m.add_child(heatmap)

    m.save("index.html") 
    # okay so now what we need to do is figure out how the fuck this heatmap stuff works


if __name__ == "__main__":
    main(sys.argv[1:])
