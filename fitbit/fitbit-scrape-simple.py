import os
import json
import csv
import sys
import datetime

# we're interested in the longest sleep each date, adjusting sleeps that
# start before noon to be considered yesterday


col_names = [
    "dateOfSleep",
    "startTime",
    "timeInBed",
    "minutesAsleep",
    "efficiency"
]
sub_col_names = ["wake", "light", "deep", "rem"]


def scrape(fnames):
    output = []
    for fname in fnames:
        if not fname.endswith(".json"):
            continue
        with open(fname) as in_file:
            for day in json.load(in_file):
                if day["type"] == "classic" and "skip" in sys.argv:
                    continue
                output.append(
                    [day[col] for col in col_names]
                    + [
                        day["levels"]["summary"].get(col, {}).get(
                            "minutes",
                            "n/a"
                        )
                        for col in sub_col_names
                    ]
                )
    return output

if __name__ == "__main__":
    with open("sleep.csv", "wb") as out_file:
        out = csv.writer(out_file)
        out.writerow(col_names + sub_col_names)
        out.writerows(scrape(os.listdir(".")))
