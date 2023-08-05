Astro Pi 2017/18 - Team Jakopičevca
===================================
Program for Astro Pi 2017/18 - Mission Space Lab - Team Jakopičevca

## Description
We would like to research how much of Slovenia (and other countries) is covered with forests. We would compare the results with previous pictures of forestation in order to determine possible deforestation or even expansion of the forests. We would also like to research light pollution with photographing at night. We would use NoIR camera in order to determine different colorization in pictures. The photographs would be analysed later.

## How It Works
The program will use Python ephem module to determine location of ISS. If ISS is flying over certain countries, the program will take pictures for a certain number of seconds and save photos in a folder with a location name. Name of the photo is time of the photo.
It's possible that ISS doesn't fly over certain countries, or if the location calculations with ephem are wrong, program will in any case take photos of Earth, but less often, and save the images in `default` folder. We will save direction of North from magnetometer due to a later analysis of photographs.
Location, sensor data, and time will be saved in the CSV file.

The locations of the photographing and other settings are stored in the `config.json` file. This file also stores TLE data, so update them before running the program.
In the `locations` section, the coordinates of countries for photographing are saved.
The value `latitude1` is the latitude of the most north point of the country, the `latitude2` is the latitude of the most south point of the country, the `longitude1` is the longitude of most west point of the country, and the `longitude2` is the longitude of the most east point of the country.
The value `delay` is the number of seconds between each photo of the country.
In the `default` section, information about photographing when the ISS is not above any country are stored.
The `delay` value is the number of seconds between each photo, and the `fallbackDelay` is the number of seconds between each photo when there is an error in obtaining an ISS location.

## Usage
The program must be used on Raspberry Pi. The program is intended for use on ISS, but could be suitable for other environments with some adjustments.

### Requirements
The program uses Python 3 and has not been tested on Python 2. It uses the following Python modules:

1. sense-hat
2. picamera
3. ephem

### Installation
It is recommended to install program in Python VENV. Python VENV must be created with `--system-site-packages` argument. However, here are general installation instructions.

Installation from PyPI:
```bash
sudo pip3 install jakopicevca
```

Installation from GitHub repository:
```bash
git clone https://github.com/filips123/jakopicevca/
cd jakopicevca
sudo python3 setup.py install
```


### Running
Create `config.json` file with the following content (fill the missing informations):
```json
{
  "TLE": [
    "ISS (ZARYA)",
    "### Get the latest ISS TLE data ###",
    "### http://www.celestrak.com/NORAD/elements/stations.txt ###"
  ],
  
  "locations": {
      "### Location Name ###": {
      "latitude1": most-north-point,
      "latitude2": most-south-point,
      "longitude1": most-west-pointt,
      "longitude2": most-east-point,
      "delay": photographing-delay
      }
  },
  
  "default": {
    "delay": default-photographing-delay,
    "fallbackDelay": fallback-photographing-delay
  }
}
```

Save the file and start the program with:
```bash
python3 -m jakopicevca path/to/config.json path/to/file.csv path/to/image/folder path/to/file.log
```

CSV and log files, and image folder will be created automatically.

## License
This project is licensed under the GNU GPL License. See the LICENSE file for more details.