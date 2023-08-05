from .jakopicevca import Jakopicevca # Our module
import argparse # For parsing the arguments
import logging # For logging
import json # For parsing the JSON file
import os # For creating the logging directory

# Parse the arguments
parser = argparse.ArgumentParser(prog = __package__, description = "Program for Astro Pi 2017/18 - Mission Space Lab - Team Jakopičevca")
parser.add_argument("config", help="the JSON config file")
parser.add_argument("csvFile", help="the CSV data file")
parser.add_argument("imgDir", help="the image directory")
parser.add_argument("logFile", help="the log file")
parser.add_argument("-c", "--colours", help="display red, green or blue to the SenseHAT display every second", action="store_true")
parser.add_argument("-t", "--datetime", help="display the date and time in the image", action="store_true")
args = parser.parse_args()

# Open the JSON file
with open(args.config) as file:
    config = json.load(file)

# Create the logging directory if it not exists
if not os.path.exists(os.path.dirname(os.path.abspath(args.logFile))):
    os.makedirs(os.path.dirname(os.path.abspath(args.logFile)))

# Set up the logging
formatter = logging.Formatter("%(asctime)s.%(msecs)d - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(args.logFile)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


# Run the our module with settings from the config file
jakopicevca = Jakopicevca(tle = config["TLE"], locations = config["locations"], default = config["default"], csvFile = args.csvFile, imgDir = args.imgDir, logger = logger, displayColours = args.colours, displayDateTime = args.datetime)
try:
    jakopicevca.run()
finally:
    jakopicevca.stop()