def get_current_location(url):
	"""
	output: database
	"""
	from hawkeye import get_data

	data = get_data(url)
	# returns: {}
	return [data["latitude"], data["longitude"]]

def get_current_weather(loc, query_name):
	from hawkeye import get_data

	latitude = loc[0]
	longitude = loc[1]

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

	url = base_url + query[query_name]
	data = get_data(url)

	return data

url = "http://freegeoip.net/json"
cur_loc = get_current_location(url)
cur_obs = get_current_weather(cur_loc, query_name="kmco")
import json
print(json.dumps(cur_obs, sort_keys=True, indent=2))
