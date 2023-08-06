# Add code here

def test(path):
	lines = tuple(open(path, 'r'))
	for line in lines:
		print(line)