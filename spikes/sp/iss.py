import csv
import skyfield
from skyfield.api import EarthSatellite, load, wgs84
from skyfield.iokit import parse_tle_file

SEATTLE = (47.6061, -122.3328)
ISS = 25544

def download_satellites():
    max_days = 7.0         # download again once 7 days old
    name = 'stations.csv'  # custom filename

    base = 'https://celestrak.org/NORAD/elements/gp.php'
    url = base + '?GROUP=stations&FORMAT=csv'

    if not load.exists(name) or load.days_old(name) >= max_days:
        load.download(url, filename=name)
        print("Downloaded new stations_file.")

def get_satellites():
    with load.open('stations.csv', mode='r') as f:
        data = list(csv.DictReader(f))

    ts = load.timescale()
    sats = [EarthSatellite.from_omm(ts, fields) for fields in data]

    return {sat.model.satnum: sat for sat in sats}, ts

def get_alt_az_dist(satellite, viewer_loc, timescale, t=None):
    if t is None:
        t = timescale.now()

    here = wgs84.latlon(*viewer_loc)
    difference = satellite - here
    topocentric = difference.at(t)
    return topocentric.altaz()
    


def main():
    sats, ts = get_satellites()
    alt, az, dist = get_alt_az_dist(sats[ISS], SEATTLE, ts)
    print("ISS:")
    print(f"Bearing   {az}")
    print(f"Elevation {alt}")
    print(f"Distance  {dist.km:.2f} km")


main()
