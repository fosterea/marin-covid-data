def get_file(path):
	with open(path, 'rb') as f:
		return f.read()
