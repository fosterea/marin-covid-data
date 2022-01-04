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
	path = 'data_storage/' + file
	try:
		file = get_file(path)
	except OSError:
		return HttpResponse(status='404')
	response = HttpResponse(file)
	
	return response