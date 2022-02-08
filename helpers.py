# Helper methods

from datetime import datetime, timedelta
import json

# Time delta of one day
DAY = timedelta(days=1)
# Age groups
AGE_GROUPS = ["0-4", "5-11", "12-18", "19-34", "35-49", "50-64", "65-74", "75-89", "90+" ]
# percent of californians under 5. This will be used
# to adjust the population so it more accuratly represents
# the risks to older people.
UNDER_5 = .06
_100K = 100000

def convert_datetime(old_date):
	"""Converts a date in a mm/dd/yyyy format into a
 	datetime object"""
	date_obj = datetime.strptime(old_date, '%m/%d/%Y')
	return date_obj

def create_date(date_string):
	"""converts a date in yyyy-mm-dd to a datetime object"""
	return datetime.strptime(date_string, '%Y-%m-%d')

def date_string(date_obj):
	"""requires datetime object and returns date
	as yyyy-mm-dd"""
	return date_obj.strftime("%Y-%m-%d")

def convert_date(old_date):
	"""converts date string formated as mm/dd/yyyy
	to a date string formated as yyyy-mm-dd"""
	return date_string(convert_datetime(old_date))

def rewind(datetime_obj):
	"""Subtracts one day from the datetime object.
	Returns the new datetime object. Kinda useless
	because you can just use datetime_obj -= DAY"""
	return datetime_obj - DAY

date1 = create_date('2021-12-25')

# Day to stop looking for data
MINIMUM_DAY = create_date('2020-03-23')

def get_date_list(now):
	"""Returns a list of datess between today and the
	minimum day. Includes the minimum day. Requires
	a datime object."""
	dates = list()
	while now > MINIMUM_DAY:
		now -= DAY
		# Append dict with date in it. Will be
		# scaffolding for future functions.
		dates.append({'date':date_string(now),})
	return dates

def add_age(dates, data):
	"""Adds the age data to the date list."""
	# Selects marin timeseries from act now covid
	cases = data['marin']
	# Age breakdown
	age_pc = data['age_distribution']
	# Marin population
	population = data['marin_population']
	# Selects the age data
	data = data['age_data']
	for day in dates:
		date = day['date']
		for group in AGE_GROUPS:
			key = date + group
			# Checks if key is in data
			# becasue they added age groups
			# over time
			if key not in data:
				continue
			day[group] = {"cases" : int(data[key]["New Confirmed Cases"])}
			day[group]['cases100k'] = day[group]['cases'] * _100K / (population * age_pc[group])
	# Estimates data for recent days
	for i in range(len(dates)):
		if AGE_GROUPS[0] in dates[i]:
			total = sum([dates[i][group]['cases'] for group in AGE_GROUPS])
			if total > 0:
				break
	breakdown = {group : dates[i][group]['cases'] / total for group in AGE_GROUPS}
	while i > 0:
		i -= 1
		if cases[dates[i]['date']]['newCases'] == None:
			del dates[i]
			continue
		new_cases = cases[dates[i]['date']]['newCases']
		for group in AGE_GROUPS:
			dates[i][group] = {"cases" : breakdown[group] * new_cases}
			dates[i][group]['cases100k'] = dates[i][group]['cases'] * _100K / (population * age_pc[group])
		

def add_vaxed_percent(dates, actuals, population, place):
	"""Adds the percent of the population that is
	vaxed to the dates list. Actuals is a dict of
	covid act now actuals for the area and population
	is the population of the area. Place is the name 
	to to put the data under in dates"""
	# Adjusts the population to show
	# risks to older people because five year olds
	# can't get the vaccine.
	population *= (1 - UNDER_5)
	vaxed = None
	i = 0
	for day in reversed(dates):
		i += 1
		# Checks if vaccinationsCompleted exists and is not null
		if 'vaccinationsCompleted' in actuals[day['date']] and actuals[day['date']]['vaccinationsCompleted'] != None:
			vaxed = actuals[day['date']]['vaccinationsCompleted'] / population
		# Adds the vaxed data.
		# Intentionally carries over
		# once data stops being avalible for
		# a date so latest days vaccination
		# rate is that of last avalible date
		if vaxed != None:
			day[f'{place}_pop'] = vaxed
	
def add_vaxed_infection_rate(dates, data):
	"""Adds the percent of cases for vaxed
	people in marin."""
	vax_data = data['vac_data']
	# Marin vaxed infection rate
	rate = None
	for day in reversed(dates):
		if day['date'] not in vax_data or 'marin_pop' not in day or day['marin_pop'] == 0 or 'ca_pop' not in day or day['ca_pop'] == 0:
			day['vax%cases'] = rate
			continue
		day_data = vax_data[day['date']]
		# This is based on the formula:
		# percent of cases = percent of people * protection
		# protection = percent of cases / percent of people
		# percent of people is writen pop.
		# The algorithm gets protection from CA data and
		# multipies it by the percent of people who are vaccinated
		# in marin to get the percent of cases that are from vaxed people.
		# Once CA data runs out it just uses the last vaxed case percent
		# for subsequent days.
		# pop = int(day_data['population_vaccinated']) / (int(day_data['population_vaccinated']) + int(day_data['population_unvaccinated']))
		pop = day['ca_pop']
		protection = get_protection(day_data, 'cases', pop)
		rate = day['marin_pop'] * protection
		day['vax%cases'] = rate

def get_protection(day, key, pop):
	"""Returns the protection for vaxed people
	in the category provided by key. ex: cases, hosp"""
	# Gets the keys to index into the data (day)
	vax_key = 'vaccinated_' + key
	un_key = 'un' + vax_key
	vaxed_percent = int(day[vax_key]) / (int(day[un_key]) + int(day[vax_key]))
	protection = vaxed_percent / pop
	return protection

def sort_cases(dates, data):
	"""Sorts cases into vaccinated and unvaccinated."""
	# Age breakdown
	age_pc = data['age_distribution']
	# Marin population
	population = data['marin_population']
	for day in dates:
		if day['vax%cases'] == None:
			break
		vaxed_p = day['vax%cases']
		un_p = 1 - vaxed_p
		vax_pop = day['marin_pop']
		un_pop = 1 - vax_pop
		for group in AGE_GROUPS:
			obj = day[group]
			# Makes vaxed and unvaxed the same for 0-4
			if group == '0-4':
				add_cases(obj, 1, 1, 'vax', population, age_pc[group])
				add_cases(obj, 1, 1, 'unvax', population, age_pc[group])
				continue
			add_cases(obj, vaxed_p, vax_pop, 'vax', population, age_pc[group])
			add_cases(obj, un_p, un_pop, 'unvax', population, age_pc[group])

def add_cases(obj, p_cases, pop, key, population, age_pc):
	obj[key + '_cases'] = obj['cases'] * p_cases
	obj[key + '_cases100k'] = obj[key + '_cases'] * _100K / (population * age_pc * pop)

def compile_data(data):
	"""Creates and returns a list with all the covid
	data broken down by vaccination and age."""
	# Get now, adjust for timezone, and get string
	# to get rid of extra hours.
	now_string = date_string(datetime.now() - timedelta(hours=8))
	# convert string into date
	now = create_date(now_string)
	# Get list of dicts holding dates
	# between now and mimimum date.
	dates = get_date_list(now)
	# Add age data to the dates
	add_age(dates, data)
	# Add marin population data
	marin_vaxed_percent(dates, data['marin_population'])
	add_vaxed_percent(dates, data['marin'], data['marin_population'], "marin")
	add_vaxed_percent(dates, data['ca'], data['ca_population'], "ca")
	
	# Add infection rates
	add_vaxed_infection_rate(dates, data)
	# Sort ceses into vaxed and unvaxed
	sort_cases(dates, data)

	# Add hosp and death data for california
	add_hosp_death_ca(dates, data['vac_data'])

	return dates

def marin_vaxed_percent(dates, population):
	"""Adds the percent of the population that is
	vaxed to the dates list. Actuals is a dict of
	covid act now actuals for the area and population
	is the population of the area. Place is the name 
	to to put the data under in dates"""
	# Adjusts the population to show
	# risks to older people because five year olds
	# can't get the vaccine.
	with open('data_storage/marin_vax.json', 'r') as f:
		pops = json.load(f)
	population *= (1 - UNDER_5)
	vaxed = None
	i = 0
	for day in reversed(dates):
		i += 1
		# Checks if vaccinationsCompleted exists and is not null
		if day['date'] in pops:
			vaxed = pops[day['date']]
		# Adds the vaxed data.
		# Intentionally carries over
		# once data stops being avalible for
		# a date so latest days vaccination
		# rate is that of last avalible date
		if vaxed != None:
			day['marin_pop'] = vaxed

def add_hosp_death_ca(dates, ca_data):
	"""Add data from chhs page about deaths and hosps in California."""
	for day in reversed(dates):

		if day['date'] not in ca_data:
			continue
		date = day['date']
		data_day = ca_data[date]

		day['cali_data'] = {}

		day['cali_data']['un_hosp/100k'] = float(data_day['unvaccinated_hosp_per_100k'])
		day['cali_data']['vax_hosp/100k'] = float(data_day['vaccinated_hosp_per_100k'])

		day['cali_data']['un_hosp/case'] = float(data_day['unvaccinated_hosp']) / float(data_day['unvaccinated_cases'])
		day['cali_data']['vax_hosp/case'] = float(data_day['vaccinated_hosp']) / float(data_day['vaccinated_cases'])

		day['cali_data']['un_deaths/100k'] = float(data_day['unvaccinated_deaths_per_100k'])
		day['cali_data']['vax_deaths/100k'] = float(data_day['vaccinated_deaths_per_100k'])

		day['cali_data']['un_deaths/case'] = float(data_day['unvaccinated_deaths']) / float(data_day['unvaccinated_cases'])
		day['cali_data']['vax_deaths/case'] = float(data_day['vaccinated_deaths']) / float(data_day['vaccinated_cases'])