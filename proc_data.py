#!/usr/bin/env pypy3
import collections
import unidecode
import csv
import unicodedata

CSV_DATAFIELD=["name", "birthday", "region", "city", "school", "grade", "CMNDNumber"]

def nameStd(name):
	name=" ".join(name.split())
	name=unidecode.unidecode(name)
	name=name.lower()
	return name

def nameSplit(name):
	name=nameStd(name)
	name=name.split()
	try:
		first_name=name[-1]
		last_name=name[0]
		middle_name=name[1:-1]
	except IndexError:
		first_name=""
		last_name=""
		middle_name=[""]
	if middle_name==[]:
		middle_name=[""]
	return (first_name, middle_name, last_name)

# I know, it looks bad, but trust me
db=dict(zip(CSV_DATAFIELD, [[] for i in range(0, len(CSV_DATAFIELD))]))

csvFile=open("crawl.csv")
csvHandler=csv.DictReader(csvFile)
counter=0

for row in csvHandler:
	for field in CSV_DATAFIELD:
		db[field].append(row[field])
	db['name'][-1]=nameStd(db['name'][-1])
	counter+=1
	if counter%491==0:
		print("Reading... %d rows\r"%(counter), end="")

print("Reading... %d rows [done]"%(counter))

counter=0
db.update({"first_name": [], "last_name": [], "middle_name": []})
for name in db['name']:
	tmp=nameSplit(name)
	first_name, middle_name, last_name=nameSplit(name)
	db['first_name'].append(first_name)
	db['last_name'].append(last_name)
	db['middle_name'].extend(middle_name)
	counter+=1
	if counter%391==0:
		print("Processing name... %d rows\r"%(counter), end="")

print("Processing name... %d rows [done]"%(counter))

for db_field in db:
	with open("%s.csv"%(db_field), "w") as out:
		outDataField=[db_field, "count"]
		outHandler=csv.DictWriter(out, fieldnames=outDataField)
		outHandler.writeheader()
		print("Writing %s.csv"%(db_field), end="")
		for entry in collections.Counter(db[db_field]).most_common():
			outHandler.writerow({db_field: entry[0], "count": entry[1]})
		print(" [done]")

print("Done")
