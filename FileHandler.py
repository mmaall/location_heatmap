import sys
import os 
import xml.etree.ElementTree as ET
import logging 
from fitparse import FitFile


class GpsDataFile():
   
    # File name contains the file that we are parsing
    # Sampling factor selects how much of the data we sample in a specific file.
    # Should be between 0 and 1 
    def __init__(self, fileName, samplingFactor = 1.0):
        self.fileName = fileName

        # We can't have a samplingFactor of zero so it is 1 if you try 0
        # TODO: Throw an error here 
        if samplingFactor == 0:
            
            # Throw an error and let generate heatmap handle it 
            samplingFactor = 1.0




        self.modValue = int(1/samplingFactor)
        strippedFileName, extension = os.path.splitext(fileName)
        self.coordinateList = []
        logging.debug("GPS Filename: {}".format(self.fileName))
        logging.debug("Sampling factor: {}".format(samplingFactor))
        logging.debug("Modulo Number: {}".format(self.modValue))
        # Parse as a gpx file 
        if extension == ".gpx":
            logging.debug("Parsing GPX file")
            self.parseGpx()
        elif extension == ".fit":
            logging.debug("Parsing FIT file")
            self.parseFit()
        else:
            err= "File type {} not supported. Unable to parse {}".format(extension, fileName)
            raise NotImplementedError(err)
  
        # Now initialize some important values
        self.calculateCenter()
        logging.debug("File Center: {}".format(self.fileCenter))

    def getCoordinates(self):
        return self.coordinateList


    # Get the mean coordinate
    # defines list fileCenter which is [x,y]

    def calculateCenter(self):
        meanX = 0.0
        meanY = 0.0

        coordinateCount = 0 
        for x, y in self.coordinateList:
            meanX += x
            meanY += y
            coordinateCount +=1

        meanX = meanX / coordinateCount
        meanY = meanY / coordinateCount

        self.fileCenter = [meanX, meanY]

    def getCenter(self):
        return self.fileCenter

    def getFirstCoordinate(self):
        return self.coordinateList[0]

    def getLastCoordinate(self):
        return self.coordinateList[-1] 

    def getCoordinateList(self):
        return self.coordinateList
    # parses a fit file
    def parseFit(self):
        coordinates = []

        try:
            fitFile = FitFile(self.fileName, check_crc = True) 
        except Exception as e:
            logging.debug("Error while parsing {} ".format(self.fileName))
            logging.debug(str(e))
            raise e

        i = 0 
        for record in fitFile.get_messages('record'):
            # iterate that counter first 
            i+=1

            # Ensures proper sampling.  
            if i % self.modValue != 0:
                continue

            # Go through all the data entries in this record
            data = record.get_values()
            logging.debug("Message data: {}".format(data))
            # must convert lat and long to degrees as well
            lat = self.convertToDegrees(data.get("position_lat"))
            lon = self.convertToDegrees(data.get("position_long"))

            logging.debug("Position: ({}, {})".format(lat, lon))
            if lat is None or lon is None:
                continue
            coordinates.append([lat,lon])

        logging.debug("Found {} coordinate pairs".format(len(coordinates)))
        self.coordinateList = coordinates

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
                i = 0 
                for trkpt in trkptNodes:
                    # iterate the counter first 
                    i += 1
                    # ensure proper sampling 
                    if i % self.modValue != 0:
                        continue

                    try:
                        # find the coordinate pair
                        coordinatePair = [trkpt.attrib["lat"], trkpt.attrib["lon"]]
                        # logging.debug("Coordinate {} appended".format(coordinatePair))

                        # append the coordinate pair to our list
                        coordinates.append(coordinatePair) 
                    except ValueError as e:
                        logging.error(str(e))
                        logging.error("Error ignored, continuing onto other data points")
        logging.debug("Coordinate scan completed")
        logging.debug("Found {} coordinate pairs".format(len(coordinates)))

        self.coordinateList = coordinates 


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

    @staticmethod

    def convertToDegrees(semicircleValue):
        return semicircleValue * (180 / pow(2,31))

    # Verifies whether the coordinates are valid or not
    # TODO: FINISH THIS, it does not work
    @staticmethod

    def checkValidCoorinate(coordinatePair):
        
        # verify a coordinate pair is passed in 
        if not isinstance(coordinatePair, list):
            # A list was not put in. Should this throw an error? 

            # TODO: Decide whether this should except or not  
            return False

        try:
            # read in the coordinate pair
            lat, lon = coordinatePair
        
        except ValueError as e:
            logging.error("Error reading coordinate pair")
            logging.error(str(e))
            logging.error("Error suppressed. Coordinate considered invalid")
            return False

        # This is broken, will return true 
        return true