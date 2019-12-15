import sys
import os 
import xml.etree.ElementTree as ET
import logging 

class GpsData():
    
    def __init__(self, fileName):
        self.fileName = fileName
        strippedFileName, extension = os.path.splitext(fileName)
        self.coordinateList = []
        logging.debug("GPS Filename: {}".format(self.fileName))
        # Parse as a gpx file 
        if extension == ".gpx":
            logging.debug("Parsing GPX file")
            self.parseGpx()
        else:
            err= "File type {} not supported. Unable to parse {}".format(extension, fileName)
            raise NotImplementedError(err)
    

    def getCoordinates(self):
        return self.coordinateList

    # parses a gpx file 
    def parseGpx(self):
        coordinates = []

        logging.debug("GPS File: {}".format(self.fileName))
        tree = ET.parse(self.fileName)
        root = tree.getroot()

        logging.debug("Parsing all children of the root looking for trk")

        trkNodes = self.findNodes(root, "trk")

        # If we haven't found the trk thing then except 
        if len(trkNodes) == 0:
            err= "GPX Parsing Error: Trk not found in GPX file".format(self.fileName)
            logging.error(err)
            raise EnvironmentError(err)

        # iterate through all the trk nodes and look for the segments 
        for trkNode in trkNodes: 
            
            trksegNodes = self.findNodes(trkNode, "trkseg")


            # now through all the segments, find the trkpoints 
            for trkSegNode in trksegNodes:

                trkptNodes = self.findNodes(trkSegNode, "trkpt") 

                for trkpt in trkptNodes:

                    try:
                        # find the coordinate pair
                        coordinatePair = (trkpt.attrib["lat"], trkpt.attrib["lon"])
                        # logging.debug("Coordinate {} appended".format(coordinatePair))

                        # append the coordinate pair to our list
                        coordinates.append(coordinatePair) 

                    except ValueError as e:
                        logging.error(str(e))
                        logging.error("Error ignored, continuing onto other data points")

        logging.debug("Coordinate scan completed")
        logging.debug("Found {} coordinate pairs".format(len(coordinates)))


    def removeNameSpaceGpx(self, inputString):
        output = inputString
        prefix, hasDelim, postfix = inputString.partition("}")

        if hasDelim:
            output = postfix

        return output

    def findNodes(self, previousNode, searchTag):
        nodes = [] 

        # search through all the children
        for child in previousNode:
            tag = self.removeNameSpaceGpx(child.tag)

            if tag == searchTag:
                nodes.append(child) 

        return nodes 
