from datetime import datetime # For the date and time
from sense_hat import SenseHat # For accessing the SenseHAT sensors and display
from picamera import PiCamera, Color # For capturing images of the Earth
import logging # For writing the log file
import csv # For writing the CSV file
import ephem # For calculating the ISS location
import sched # For capturing images every x seconds
import math # For the mathematical functions (converting between degrees and radians)
import time # For the time functions
import os # For creating the data directories

class Jakopicevca:
    def __init__(self, tle, locations, default, csvFile, imgDir, logger, displayColours, displayDateTime): # Set up the program
        self.locations = locations
        self.default = default
        self.imgDir = imgDir
        self.logger = logger
        self.displayColours = displayColours
        self.displayDateTime = displayDateTime
        self.error = False
        
        # Create the image directory if it not exists
        if not os.path.exists(self.imgDir):
            os.makedirs(self.imgDir)
        
        # Set up the CSV file for sensor and location data
        if not os.path.exists(os.path.dirname(os.path.abspath(csvFile))):
            os.makedirs(os.path.dirname(os.path.abspath(csvFile)))
        exists = os.path.isfile(csvFile)
        self.csvFile = open(csvFile, mode = "a+", newline = "")
        self.writer = csv.DictWriter(self.csvFile, fieldnames = ["datetime", "latitude", "longitude", "location", "daynignt", "compass"])
        if not exists:
            self.writer.writeheader()
        
        # Parse the ISS TLE data into ephem
        self.iss = ephem.readtle(tle[0], tle[1], tle[2])
        
        # For the calculation if it is day or night
        self.sun = ephem.Sun()
        self.twilight = math.radians(-6)
        
        # Set up the camera
        self.camera = PiCamera()
        self.camera.annotate_background = Color('Black')
        
        # Set up the SenseHAT
        self.sense = SenseHat()
        self.sense.rotation = 270
        
        # Set up the scheduler
        self.scheduler = sched.scheduler(time.time, time.sleep)
    
    def run(self): # Run the program
        # Set functions for all locations to the scheduler
        if self.displayColours:
            self.scheduler.enter(0, 1, self.displayColour, (255, 0, 0)) # For display colours to the SenseHAT display
        self.scheduler.enter(0, 1, self.captureImage) # For default capturing images
        for locationName, locationData in self.locations.items():
            self.scheduler.enter(0, 1, self.captureImage, (locationName, locationData)) # For capturing images on locations
        
        self.logger.info("Program started.")
        
        # Run the scheduler
        self.scheduler.run()
    
    def stop(self): # Stop the program
        # Cancel the all events
        list(map(self.scheduler.cancel, self.scheduler.queue))
        
        # Clear the SenseHAT display
        self.sense.clear()
        
        self.logger.info("Program stopped.")
    
    def captureImage(self, locationName = "", locationData = {}): # Capture image and collect data
        if locationName == "" and locationData == {}:
            self.scheduler.enter(self.default["delay"], 1, self.captureImage) # Run the program again in self.default["delay"] seconds
        else:
            self.scheduler.enter(locationData["delay"], 1, self.captureImage, (locationName, locationData)) # Run the program again in locationData["delay"] seconds
        
        # Get the UTC time and timestamp
        utcnow = datetime.utcnow()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Try to get the ISS location with ephem
        try:
            self.iss.compute(utcnow)
        # Run this if the TLE data are outdated
        except ValueError as e:
            # If the error has not yet been written, it is written to the log
            if self.error == False:
                self.logger.error(e)
                self.error = True
        
        if self.error == True:
            # Cancel the previous scheduler events
            events = list()
            for event in self.scheduler.queue:
                if event[2] != self.displayColour:
                    events.append(event)
            list(map(self.scheduler.cancel, events))
            
            # Run the program again in self.default["fallbackDelay"] seconds
            self.scheduler.enter(self.default["fallbackDelay"], 1, self.captureImage)
            
            # Create the image directory if it not exists
            imagePath = os.path.join(self.imgDir, "default")
            if not os.path.exists(imagePath):
                os.makedirs(imagePath)
            
            # Capture the image
            if self.displayDateTime:
                self.camera.annotate_text = timestamp
            self.camera.capture(os.path.join(imagePath, timestamp + ".jpg"))
            
            # Write the data to the CSV and log files
            self.logger.info("Capturing. Degrees from North: %f" % (self.sense.compass))
            self.writer.writerow({"datetime": timestamp, "latitude": "", "longitude": "", "location": "", "daynignt": "", "compass": self.sense.compass})
            self.csvFile.flush()
            os.fsync(self.csvFile.fileno())
            
            return None
        
        # For calculation if it is day or night
        observer = ephem.Observer()
        observer.lat = self.iss.sublat
        observer.long = self.iss.sublong
        observer.elevation = 0
        
        # Calculate if it is day or night
        self.sun.compute(observer)
        sunAngle = math.degrees(self.sun.alt)
        day = True if sunAngle > self.twilight else False
        
        if locationName == "" and locationData == {}:
            # Create the image directory if it not exists
            imagePath = os.path.join(self.imgDir, "default")
            if not os.path.exists(imagePath):
                os.makedirs(imagePath)
            
            # Capture the image
            if self.displayDateTime:
                self.camera.annotate_text = timestamp
            self.camera.capture(os.path.join(imagePath, timestamp + ".jpg"))
            
            # Write the data to the CSV and log file
            self.logger.info("Capturing. Latitude: %f - Longitude: %f - %s - Degrees from North: %f" % (math.degrees(self.iss.sublat), math.degrees(self.iss.sublong), ("Day" if day else "Night"), self.sense.compass))
            self.writer.writerow({"datetime": timestamp, "latitude": math.degrees(self.iss.sublat), "longitude": math.degrees(self.iss.sublong), "location": "", "daynignt": ("day" if day else "night"), "compass": self.sense.compass})
            self.csvFile.flush()
            os.fsync(self.csvFile.fileno())
        
        else:
            if (float(locationData["latitude1"]) >= float(math.degrees(self.iss.sublat)) >= float(locationData["latitude2"])) and (float(locationData["longitude1"]) <= float(math.degrees(self.iss.sublong)) <= float(locationData["longitude2"])): # If the ISS is flying over the country
                # Create the image directory if it not exists
                imagePath = os.path.join(self.imgDir, locationName)
                if not os.path.exists(imagePath):
                    os.makedirs(imagePath)
                
                # Capture the image
                if self.displayDateTime:
                    self.camera.annotate_text = timestamp
                self.camera.capture(os.path.join(imagePath, timestamp + ".jpg"))
                
                # Write the data to the CSV and log file
                self.logger.info("Capturing. %s - Latitude: %f - Longitude: %f - %s - Degrees from North: %f" % (locationName, math.degrees(self.iss.sublat), math.degrees(self.iss.sublong), ("Day" if day else "Night"), self.sense.compass))
                self.writer.writerow({"datetime": timestamp, "latitude": math.degrees(self.iss.sublat), "longitude": math.degrees(self.iss.sublong), "location": locationName, "daynignt": ("day" if day else "night"), "compass": self.sense.compass})
                self.csvFile.flush()
                os.fsync(self.csvFile.fileno())
    
    def displayColour(self, red, green, blue): # Display red, green and blue to the SenseHAT display every second
        # Display red, green or blue to the SenseHAT display next second
        if red == 255:
            self.scheduler.enter(1, 1, self.displayColour, (0, 255, 0))
        elif green == 255:
            self.scheduler.enter(1, 1, self.displayColour, (0, 0, 255))
        elif blue == 255:
            self.scheduler.enter(1, 1, self.displayColour, (255, 0, 0))
        
        # Display colour to the SenseHAT display
        self.sense.clear(red, green, blue)