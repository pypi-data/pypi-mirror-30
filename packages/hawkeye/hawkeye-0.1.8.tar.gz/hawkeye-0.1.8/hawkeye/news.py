from hawkeye import *
import requests

def NewsAPI():

	_base = "https://newsapi.org/v2/"
	_top = "/top-headlines?"
	_all = "/everything?"
	# _source = "sources=abc-news&"
	_source = "sources=fox-news&"
	_country = "country=us&"
	_apikey = "apiKey=686cabe9d8ae4b1b8ea39ca439563f8a"

	_url = _base + _top + _source + _apikey

	_data = get_json(_url)
	print_data(_data)

