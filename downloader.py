# Donloads csv and turns them into json files.


import csv
import requests
import urllib, json
import time
from helpers import convert_date, compile_data, AGE_GROUPS

SECONDS_IN_HOUR = 3600

# Makes sure the data has been updated within
# an hour and returns the data as a json
def load_data():
	now = time.time()
	data = load_json()
	if data['updated'] < now - SECONDS_IN_HOUR:
		update_data()
		data = load_json()
	return data

# Loads the json file
def load_json():
	with open('data_storage/data.json') as f:
		data = json.load(f)
		return data

# Downlods the csv and turns it into a json file
def update_data():
	# Dict that is turned into a json file
	data = dict()

	now = time.time()
	# Recored last update
	data['updated'] = now

	# # Downloads age data from california
	# DEM_CSV_URL = 'https://data.chhs.ca.gov/dataset/f333528b-4d38-4814-bebb-12db1f10f535/resource/e2c6a86b-d269-4ce1-b484-570353265183/download/covid19casesdemographics.csv'

	# with requests.Session() as s:
	#     download = s.get(DEM_CSV_URL)

	#     decoded_content = download.content.decode('utf-8')

	# # Really stupid but I couldn't figure out how to
	# # dict read the data from decoded_content so I put it
	# # in a csv.
	# with open('demographics.csv', 'w') as f:
	# 	f.write(decoded_content)

	# with open('demographics.csv', 'r') as f:

	# 	reader = csv.DictReader(f)

	# 	age_data = dict()

	# 	for row in reader:
	# 		if (row['demographic_category'] == 'Age Group'):
	# 			if (row['demographic_value'] not in age_data):
	# 				age_data[row['demographic_value']] = list()
	# 			age_data[row['demographic_value']].append(row)

	# data['age_data'] = age_data

	# Downodes age data from marin county
	AGE_URL = 'https://data.marincounty.org/api/views/rucx-nsrq/rows.csv?accessType=DOWNLOAD'
	age_data = dict()

	with requests.Session() as s:
	    download = s.get(AGE_URL)

	    decoded_content = download.content.decode('utf-8')
		
	# Really stupid but I couldn't figure out how to
	# dict read the data from decoded_content so I put it
	# in a csv.
	with open('data_storage/demographics.csv', 'w') as f:
		f.write(decoded_content)

	with open('data_storage/demographics.csv', 'r') as f:

		reader = csv.DictReader(f)

		for row in reader:
			age_data[convert_date(row['TestDate']) + row['Age Group']] = row

	data['age_data'] = age_data


	# Downloads vaccine data from california
	VAC_URL = 'https://data.chhs.ca.gov/dataset/e39edc8e-9db1-40a7-9e87-89169401c3f5/resource/c5978614-6a23-450b-b637-171252052214/download/covid19postvaxstatewidestats.csv'

	vac_data = dict()

	with requests.Session() as s:
	    download = s.get(VAC_URL)

	decoded_content = download.content.decode('utf-8')

	with open('data_storage/demographics.csv', 'w') as f:
		f.write(decoded_content)

	with open('data_storage/demographics.csv', 'r') as f:

		reader = csv.DictReader(f)

		for row in reader:
			
			if 'date' in row:
				vac_data[row['date']] = row
				continue

			row['DATE'] = row['\ufeffDATE']
			del row['\ufeffDATE']

			for key in row.copy().keys():
				row[key.lower()] = row[key]
				del row[key]
			vac_data[row['date']] = row

	VAC_URL = 'https://data.chhs.ca.gov/dataset/e39edc8e-9db1-40a7-9e87-89169401c3f5/resource/39969fac-02c6-4dc5-967f-0d1438a91f81/download/covid19postvaxstatewidestats_111321.csv'

	with requests.Session() as s:
	    download = s.get(VAC_URL)

	decoded_content = download.content.decode('utf-8')

	with open('data_storage/demographics.csv', 'w') as f:
		f.write(decoded_content)

	with open('data_storage/demographics.csv', 'r') as f:

		reader = csv.DictReader(f)

		for row in reader:
			
			if 'date' in row:
				vac_data[row['date']] = row
				continue

			row['DATE'] = row['\ufeffDATE']
			del row['\ufeffDATE']

			for key in row.copy().keys():
				row[key.lower()] = row[key]
				del row[key]
			vac_data[row['date']] = row
			
	data['vac_data'] = vac_data

	# Puts the age distribution data in data dict
	with open('data_storage/ages.json') as f:
		data['age_distribution'] = json.load(f)

	# Downloads marin data from covid act now
	marin_url = "https://api.covidactnow.org/v2/county/06041.timeseries.json?apiKey=8ea300e5026849ccaa2f34065f4be3d8"
	response = urllib.request.urlopen(marin_url)
	marin = json.loads(response.read())
	# make it a dict soratable by date
	actuals = marin['actualsTimeseries']
	marin_dict = dict()
	for day in actuals:
		marin_dict[day['date']] = day
	data['marin'] = marin_dict
	data['marin_population'] = marin["population"]

	# Downloads california data from covid act now
	ca_url = "https://api.covidactnow.org/v2/state/CA.timeseries.json?apiKey=8ea300e5026849ccaa2f34065f4be3d8"
	response = urllib.request.urlopen(ca_url)
	ca = json.loads(response.read())
	# make it a dict soratable by date
	actuals = ca['actualsTimeseries']
	ca_dict = dict()
	for day in actuals:
		ca_dict[day['date']] = day
	data['ca'] = ca_dict
	data['ca_population'] = ca['population']

	with open('marin.json', 'w') as f:
		json.dump(data, f)

	# Process data
	breakdown = {"data":compile_data(data)}
	breakdown['updated'] = data['updated']

	# Add series for graphs
	add_series(breakdown)
	add_cali_data(breakdown)
	# Stores the data in data_storage/data.json
	with open('data_storage/data.json', 'w') as f:
		json.dump(breakdown, f)

def add_series(data):
	"""Add series data to data for charting.js."""
	series = {}
	for group in AGE_GROUPS:
		series[group] = {"vaxed": [], "unvaxed" : []}
	i = len(data['data'])
	for day in data['data']:
		for group in AGE_GROUPS:
			
			if 'vax_cases100k' not in day[group] or group == '0-4':
				series[group]['unvaxed'].append({'x': day['date'], 'y': day[group]['cases100k']})
				continue
			series[group]['vaxed'].append({'x': day['date'], 'y': day[group]['vax_cases100k']})
			series[group]['unvaxed'].append({'x': day['date'], 'y': day[group]['unvax_cases100k']})
		i -= 1

	for group in series:
		
		for i in range(len(series[group]['vaxed'])):
			series[group]['vaxed'][i]['y'] = _7day_average(series[group]['vaxed'], i)
		for i in range(len(series[group]['unvaxed'])):
			series[group]['unvaxed'][i]['y'] = _7day_average(series[group]['unvaxed'], i)

	data['series'] = series

def _7day_average(days, day_num):
	sum = 0
	number = 0
	for day in days[day_num:]:
		sum += day['y']
		number += 1
		if number == 7:
			break
	return sum / number


def add_cali_data(data):

	vax_hosps_k = []	
	un_hosps_k = []	
	vax_hosps_c = []	
	un_hosps_c = []	

	vax_deaths_k = []	
	un_deaths_k = []	
	vax_deaths_c = []	
	un_deaths_c = []


	for day in data['data']:

		if 'cali_data' not in day:
			continue

		vax_hosps_k.append({'x': day['date'], 'y': day['cali_data']['vax_hosp/100k']})
		un_hosps_k.append({'x': day['date'], 'y': day['cali_data']['un_hosp/100k']})
		vax_hosps_c.append({'x': day['date'], 'y': day['cali_data']['vax_hosp/case']})
		un_hosps_c.append({'x': day['date'], 'y': day['cali_data']['un_hosp/case']})

		vax_deaths_k.append({'x': day['date'], 'y': day['cali_data']['vax_deaths/100k']})
		un_deaths_k.append({'x': day['date'], 'y': day['cali_data']['un_deaths/100k']})
		vax_deaths_c.append({'x': day['date'], 'y': day['cali_data']['vax_deaths/case']})
		un_deaths_c.append({'x': day['date'], 'y': day['cali_data']['un_deaths/case']})
		

	serieses = [
		vax_hosps_k,	
		un_hosps_k,
		vax_hosps_c,	
		un_hosps_c,

		vax_deaths_k,
		un_deaths_k,
		vax_deaths_c,
		un_deaths_c,
	]


	for series in serieses:
		for i in range(len(series)):
			series[i]['y'] = _7day_average(series, i)
	
	
	serieses = []

	serieses.append({
		'series': [
			{'points' : vax_hosps_k, 'name' : 'vaxed'},
			{'points' : un_hosps_k, 'name' : 'unvaxed'},
			], 
		'lable': 'hosps/100k',
		'units' : 'hospitalizations/100k',
		'msg' : 'Hospitalizations per 100k in California (7 day average)'
		})

	serieses.append({
		'series': [
			{'points' : vax_hosps_c, 'name' : 'vaxed'},
			{'points' : un_hosps_c, 'name' : 'unvaxed'},
			], 
		'lable': 'hosps/case',
		'units' : 'hospitalizations/case',
		'msg' : 'Hospitalizations per case in California (7 day average)'
		})

	serieses.append({
		'series': [
			{'points' : vax_deaths_k, 'name' : 'vaxed'},
			{'points' : un_deaths_k, 'name' : 'unvaxed'},
			], 
		'lable': 'deaths/100k',
		'units' : 'deaths/100k',
		'msg' : 'Deaths per 100k in California (7 day average)'
		})

	serieses.append({
		'series': [
			{'points' : vax_deaths_c, 'name' : 'vaxed'},
			{'points' : un_deaths_c, 'name' : 'unvaxed'},
			], 
		'lable': 'deaths/case',
		'units' : 'deaths/case',
		'msg' : 'Deaths per case in California (7 day average)'
		})

	data['cali_data'] = serieses