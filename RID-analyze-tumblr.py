### this document uses 'anal' as short for 'analyze'

import rid
import json
import csv
from collections import defaultdict as dd
from pdb import pm

#initalize RID --- copied (almost) directly from rid.py
rider = rid.RegressiveImageryDictionary()
rider.load_dictionary_from_string(rid.DEFAULT_RID_DICTIONARY)
rider.load_exclusion_list_from_string(rid.DEFAULT_RID_EXCLUSION_LIST)
rid=rider
del rider

db = json.load(open("all-posts.json"))
# [(date, post), ...]


category_names = set()

def anal_post(post):
    date, post = post
    results = rid.analyze(post)
    out = {catergory.full_name(): count for catergory,count in results.category_count.items()}
    category_names.update(out.keys()) 
    out["date"] = date
    out["length"] = results.word_count
    return out 

results = [anal_post(row) for row in db]
cols =  ["date", "length"] + sorted(list(category_names))

writer = csv.DictWriter(open("anal.csv", 'w'), fieldnames=cols, restval=0)
writer.writeheader()
writer.writerows(results)





