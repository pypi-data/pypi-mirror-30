from re import search
from os import urandom

def random(limit=10, regex='[\w -~]'):
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
	while True:
		try:
			g = int(random(int(len(str(num))+1), regex='[0-9]*'))
		except ValueError:
			continue
		if g > int(num):
			return g

def lowerrand(num):
	while True:
		try:
			g = int(random(int(len(str(num))), regex='[0-9]*'))
		except ValueError:
			continue
		if g > 1 and g < int(num):
			return g

def randin(top, low=0):
	if low:
		low, top = top, low
	while True:
		try:
			g = int(random(int(len(str(top))), regex='[0-9]*'))
		except ValueError:
			continue
		if g > int(low) and g < int(top):
			return g


def dhrands(sec):
	rnd = biggerrand(sec)
	return rnd, maxprime(rnd)
