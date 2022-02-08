from typing import get_args
from webbrowser import get
from django.http import HttpResponse
from django.shortcuts import render
from api import get_file
from downloader import load_data, AGE_GROUPS

def index(request):
	context = {'groups' : AGE_GROUPS}
	return render(request, 'mysite/index.html', context)


def api(request, file):
	if file == 'data.json':
		load_data()
	try:
		file = get_file(file)
	except OSError:
		return HttpResponse(status='404')
	response = HttpResponse(file)
	
	return response