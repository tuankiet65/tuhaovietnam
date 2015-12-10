#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import csv
import time

def getHTML(url):
	global ses
	while True:
		try:
			html=ses.get(url)
			html.raise_for_status()
			html=BeautifulSoup(html.text, "html.parser")
		except Exception as e:
			print("\nException caught")
			print("Sleeping for 10 sec before retrying")
			time.sleep(10)
			ses=requests.Session()
			continue
		except requests.exceptions.ConnectionError:
			print("Making new session")
			ses=requests.Session()
			continue
		break
	return html

def getNumberOfAccounts():
	html=getHTML("http://tuhaovietnam.com.vn/thisinh.html")
	html=html.find_all("table")[0] # Get account table
	html=html.find_all("td")[0] # Get first ID in table
	return int(html.string)

def createNewFile(filename):
	with open(filename, 'w') as csvFile:
		csvHandler=csv.DictWriter(csvFile, fieldnames=CSV_DATAFIELD, quoting=csv.QUOTE_MINIMAL);
		csvHandler.writeheader()

def getCurrID(filename):
	''' For resume support '''
	try:
		csvFile=open(filename, "r")
	except Exception as e:
		createNewFile(filename)
		return 0
	csvHandler=csv.DictReader(csvFile, fieldnames=CSV_DATAFIELD, quoting=csv.QUOTE_MINIMAL)
	idNum=0
	print("Resuming...")
	for data in csvHandler:
		if data["id"]=="id":
			continue
		if int(data["id"])!=idNum+1:
			raise Exception("Mismatch ID number: expect %s but got %s"%(idNum+1, data["id"]))
		idNum=int(data["id"])
	return idNum

def getIDData(ID):
	availableFields={
						"Khu vực": "region",
						"Thành phố": "city",
						"Trường": "school",
						"Lớp": "grade",
						"Số CMND/Thẻ học sinh": "CMNDNumber",
						"Họ và tên": "name",
						"Idgame": "username", 
						"Ngày sinh": "birthday"
					}
	res={}
	html=getHTML("http://tuhaovietnam.com.vn/thisinh.html?cmd=detail&id=%s"%(ID))
	html=html.find_all(class_="thisinh-content")[0] # Get main div
	html=html.find_all(class_="div-content form-horizontal form-search")[0] # Get info div
	grabFlag=False
	grabFieldname=""
	for string in html.stripped_strings:
		if grabFlag:
			grabFlag=False
			if (availableFields.get(string) is None):
				res.update({grabFieldname: string})
				continue
		if (availableFields.get(string) is not None):
			grabFlag=True
			grabFieldname=availableFields.get(string)
	res["id"]=ID
	return res

# Constants
ses=requests.Session()
FILENAME="crawl.csv"
CSV_DATAFIELD=["id", "name", "username", "birthday", "region", "city", "school", "grade", "CMNDNumber"]

# Get ID Range
idFrom=getCurrID(FILENAME)+1
idTo=getNumberOfAccounts()
print("Start crawling from ID %d to %d"%(idFrom, idTo))

# Open output csv
csvFile=open(FILENAME, "a")
csvHandler=csv.DictWriter(csvFile, fieldnames=CSV_DATAFIELD, quoting=csv.QUOTE_MINIMAL)

try:
	for ID in range(idFrom, idTo+1):
		print("\rFetching ID %s"%(ID), end="")
		data=getIDData(ID)
		if (ID%10==0):
			print()
			print(data);
		csvHandler.writerow(data)
		csvFile.flush()
		time.sleep(1)
except KeyboardInterrupt:
	print("\nInterrupt signal caught, exiting...")
finally:
	csvFile.close()