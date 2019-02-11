import os
import json
import csv
from datetime import datetime, timedelta

# we're interested in the longest sleep each date, adjusting sleeps that
# start before noon to be considered yesterday

# we're _not_ interested in naps, at least at this time
# because we're mostly interested in studying the effects of caffeine on
# sleep that night (not the next day)
# and naps make figuring anything out difficult

# however, if we *were* studying total sleep time or just efficiency
# naps could be interesting


col_names = [
    "date",
    "startTime",
    "timeInBed",
    "minutesAsleep",
    "efficiency"
]
sub_col_names = ["wake", "light", "deep", "rem", "awake", "restless", "asleep"]






output = []
for fname in os.listdir("."):
    if not fname.endswith(".json"):
        continue
    with open(fname) as in_file:
        big_sleep = {"timeInBed": 0}
        today = None
        for sleep in json.load(in_file):
            stamp = datetime.strptime(sleep["startTime"], "%Y-%m-%dT%H:%M:%S.%f")
            # check if it should be associated with the previous date
            # (it's a nap or late bedtime)
            if stamp.hour > 18:
                date = stamp.date()
                sleep["date"] = date
            else:
                date = stamp.date() - timedelta(1)
                sleep["date"] = date

            # for everything that's the same day, check if it's the biggest
            if date == today:
                if big_sleep["timeInBed"] < sleep["timeInBed"]:
                    print "decided {} {} was b i g er than {} {}".format(sleep["startTime"], sleep["timeInBed"], big_sleep["startTime"], big_sleep["timeInBed"])
                    big_sleep = sleep
                else:
                    print "decided {} {} was smoler than {} {}".format(sleep["startTime"], sleep["timeInBed"], big_sleep["startTime"], big_sleep["timeInBed"])
            else:
                if today is not None:
                    output.append(
                        [big_sleep[col] for col in col_names]
                        + [
                            big_sleep["levels"]["summary"].get(col, {}).get(
                                "minutes",
                                "n/a"
                            )
                            for col in sub_col_names
                        ]
                    )
                big_sleep = sleep
                today = date



with open("sleep.csv", "wb") as out_file:
    out = csv.writer(out_file)
    out.writerow(col_names + sub_col_names)
    output.sort()
    out.writerows(output)
