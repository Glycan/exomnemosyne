"""goes through google location history takeout json and outputs a CSV of
whether you've been within a certain distance of certin addresses that for
each day"""
from __future__ import division
from datetime import datetime
from collections import namedtuple, defaultdict
from itertools import takewhile
import argparse
import csv
import calendar

import ijson.backends.yajl2_cffi as ijson
from geopy.distance import geodesic
import geocoder

# worthwhile optimizations:
# - use the raw timestamps instead of dates
# - instead of geodeisc, use a bounding box like
#   https://github.com/jfein/PyGeoTools/blob/master/geolocation.py


# "home" "home address" 0.5mi "work" "work address 0.5mi --from "0/1/1" --to ..
# -> date, home, work\n11/1/1,True,False

Point = namedtuple("Point", "latitude, longitude, date")
Addr = namedtuple("Addr", "latitude, longitude, name, dist")


def valid_date(s):
    "argparse date type validation"
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


parser = argparse.ArgumentParser(
    description="says which days you were near which addresses"
)
parser.add_argument(
    "-a", "--addr", "--address",
    nargs=3,
    action="append",
    dest="addrs",
    metavar=("address-name", "address", "distance from address (km)")
)
parser.add_argument("--start", type=valid_date, default=valid_date("2000-1-1"))
parser.add_argument("--stop", required=False, type=valid_date, default=datetime.now().date())
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument("-o", "--output", default="locations.csv")
args = parser.parse_args()

if args.debug:
    print("looking at addresses {} from {} to {}".format(
        repr(args.addrs),
        args.start,
        args.stop
    ))
    from pdb import pm


addrs = []
for addr in args.addrs:
    place = geocoder.osm(addr[1])
    addrs.append(Addr(place.lat, place.lng, addr[0], float(addr[2])))

# depricated, kept for testing purposes
def read_points():
    with open("../Location History.json") as f:
        for point in ijson.items(f, "locations.item"):
            yield Point(
                point["latitudeE7"] / 10 ** 7,
                point["longitudeE7"] / 10 ** 7,
                datetime.fromtimestamp(int(point["timestampMs"]) / 1000).date()
            )

with open(args.output, "w") as o:
    out = csv.writer(o)
    out.writerow(["date"] + [addr.name for addr in addrs])

    day = [args.stop] + [False for addr in addrs]
    n = 0

    if args.debug:
        print "starting points crunching"

    rows = []
    with open("../Location History.json") as f:
        for point in ijson.items(f, "locations.item"):
            point = Point(
                point["latitudeE7"] / 10 ** 7,
                point["longitudeE7"] / 10 ** 7,
                datetime.fromtimestamp(int(point["timestampMs"]) / 1000).date()
            )
            # it goes from most recent (large values) to oldest (small values)
            if point.date > args.stop:
                continue
            if point.date < args.start:
                break
            if day[0] > point.date:
                rows.append(day)
                if args.debug:
                    print "wrote {} with {} points".format(
                        day[0].strftime("%Y-%m-%d"),
                        n
                    )
                day = [point.date] + [False for addr in addrs]
                n = 0
            for i, addr in enumerate(addrs):
                if geodesic(addr[:2], point[:2]).km <= addr.dist:
                    day[i + 1] = True
                    continue
            n += 1
    out.writerows(reversed(rows))

