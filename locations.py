"""goes through google location history takeout json and outputs a CSV of
whether you've been within a certain distance of certin addresses that for
each day"""
from __future__ import division
from datetime import datetime
from collections import namedtuple, defaultdict
from itertools import takewhile
import json
import argparse
import csv

from geopy.distance import geodesic
import geocoder

# "home" "home address" 0.5mi "work" "work address 0.5mi --from "0/1/1" --to ..
# -> date, home, work\n11/1/1,True,False

Point = namedtuple("Point", "latitude, longitude, date")
Addr = namedtuple("Addr", "latitude, longitude, name, dist")


def valid_date(s):
    "argparse date type validation"
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def read_points():
    "../Location History.json -> Point generator"
    with open("../Location History.json") as f:
        data = json.load(f)

    for point in data["locations"]:
        yield Point(
            point["latitudeE7"] / 10 ** 7,
            point["longitudeE7"] / 10 ** 7,
            datetime.fromtimestamp(int(point["timestampMs"]) / 1000).date()
        )

def main():
    parser = argparse.ArgumentParser(
        description="says which days you were near which addresses"
    )
    parser.add_argument(
        "--addr", "-a",
        nargs=3,
        action="append",
        dest="addrs",
        metavar=("address-name", "address", "distance from address (km)")
    )
    parser.add_argument("--start", type=valid_date, default=valid_date("2000-1-1"))
    parser.add_argument("--stop", required=False, default=datetime.now())
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        print("looking at addresses {} from {} to {}".format(
            repr(args.addrs),
            args.start,
            args.stop
        ))

    addrs = []
    for addr in args.addrs:
        place = geocoder.osm(addr[1])
        addr.append(Addr(place.lat, place.lng, addr[0], addr[2]))

    points = takewhile(
        lambda point: args.start <= point.datetime <= args.stop,
        read_points()
    )

    days = defaultdict(lambda : {addr.name: False for addr in addrs}, {})

    for point in points:
        for addr in addrs:
            if geodesic(addr[:2], point[:2]).km <= addr.dist:
                days[addr.date][addr.name] = True

    with open("locations.csv", "w") as f:
        csv.writer(f).writerows(
            [["date"] + [addr.name for addr in addrs]] +
            [[date] + [values[addr.name] for addr in addrs]
             for date, values in sorted(days.items())]
        )

if __name__ == "__main__":
    main()
