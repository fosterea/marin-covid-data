def get_file(file):
	path = 'data_storage/' + file
	with open(path, 'rb') as f:
		file =  f.read()
	return file
	
