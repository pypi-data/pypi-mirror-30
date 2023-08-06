"""randomisation functions"""
from re import search
from os import urandom

def random(limit=10, regex=r'[\w -~]'):
	"""random character by limit"""
	retstr = ''
	while True:
		try:
			out = urandom(1).decode()
		except UnicodeDecodeError:
			continue
		try:
			if search(regex, out).group(0):
				retstr = '%s%s'%(retstr, out.strip())
		except AttributeError:
			continue
		if len(retstr) >= int(limit):
			break
	return retstr

def biggerrand(num):
	"""greater random number"""
	while True:
		try:
			g = int(random(int(len(str(num))+1), regex=r'[0-9]*'))
		except ValueError:
			continue
		if g > int(num):
			break
	return g

def lowerrand(num):
	"""lower random number"""
	while True:
		try:
			g = int(random(int(len(str(num))), regex=r'[0-9]*'))
		except ValueError:
			continue
		if g > 1 and g < int(num):
			break
	return g

def randin(top, low=0):
	"""number in between low and top"""
	if low:
		low, top = top, low
	while True:
		try:
			g = int(random(int(len(str(top))), regex=r'[0-9]*'))
		except ValueError:
			continue
		if g > int(low) and g < int(top):
			break
	return g
