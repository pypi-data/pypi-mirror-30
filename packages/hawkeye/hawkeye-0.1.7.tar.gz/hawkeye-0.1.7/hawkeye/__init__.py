from time import strftime

__author__ = "Todd Jarolimek II"
__version__ = "0.1.7"

# from .functions import *
# from .location import *
# from .weather import *
# from .dataobject import *

"""
FUNCTIONS
"""

#1

def date():
	from time import strftime
	return strftime("%Y-%m-%d")

def time():
	from time import strftime
	return strftime("%H:%M:%S")

def data_to_csv(data_series, filename):
	import csv
	with open(filename, "w") as csvfile:
		_write = csv.writer(csvfile, lineterminator="\n")
		for key in data_series.keys():
			_write.writerow([key, data_series[key]])
#5
def list_to_str(pylist, delimiter):
	pylist_str = ""
	for i in range(len(pylist)):
		if type(i) != type("str"):
			pylist[i] = str(pylist[i])
		if i == (len(pylist) - 1):
			pylist_str += pylist[i]
		else:
			pylist_str += pylist[i]
			pylist_str += delimiter
	return pylist_str
#6
def string_to_char_list(string):
	def main(string):
		index = 0
		char_list = []
		for char in string:
			char_list += char

		return char_list

	if type(string) == type([]):
		string_array = string
		return_array = []
		for string in string_array:
			return_array.append(main(string))
		return return_array
	else:
		return main(string)
#7
def list_from_data(charset):
	pylist = []
	for key in charset.keys():
		temp = charset[key]
		for char in temp:
			pylist.append(char)

	return pylist

def get_data(url):

	import requests
	import json

	request = requests.get(url)
	data = json.loads(request.text)

	return data

def navigate(data):
	while(True):
		try:
			key_list = list(data.keys())
			for i,v in enumerate(key_list):
				print(str(i) + "\t" + str(v))
			conin = input(">>>")
			data = data[key_list[int(conin)]]
		except:
			print("That's the end of the tree.")
			break

def open_data(filename):
	_ext = filename.split(".")
	_ext = _ext.pop()
	if _ext == "json":
		import json
		with open(filename, "r") as file:
			data = json.load(file)
		return data

def save_data(data, filename):
	_ext = filename.split(".")
	_ext = _ext.pop()
	if _ext == "json":
		with open(filename, "w") as file:
			json.dump(data, file)
		return True

def print_data(data):
	print(json.dumps(data, sort_keys=True, indent=2))

"""
2. Location
"""
class Location:

	def __init__(self):
		self._url = "http://freegeoip.net/json"

	def get_current_location(self):
		"""
		output: database
		"""
		from hawkeye import get_data

		data = get_data(self._url)
		# returns: {}
		return data

"""
3. Weather
"""
class NOAA:

	def __init__(self, latitude, longitude, query):
		self._latitude = latitude
		self._longitude = longitude
		self._query = query

	def get_current(self):
		from hawkeye import get_data

		base_url = 'http://api.weather.gov'

		# Metadata query
		query = {}
		query["metadata"] = "/points/" + str(latitude)+ "," + str(longitude)
		query["forecast"] = {}
		query["forecast"]["current"] = query["metadata"] + "/forecast"
		query["forecast"]["hourly"] = query["forecast"]["current"] + "/hourly"
		query["stations"] = query["metadata"] + "/stations"
		query["kmco"] = "/stations/kmco/observations/current"
		query["kmlb"] = "/stations/kmlb/observations/current"
		query["zone-alerts"] = "/alerts/active/zone/FLZ045"
		query["area-alerts"] = "/alerts/active/area/FL"
		query["test"] = "/alerts/active/zone/OHC001"
		query["all-alerts"] = "/alerts/active/count"

		# My zone: FLZ045

		url = base_url + query
		data = get_data(url)

		return data

"""
4. FUNCTIONS
"""









