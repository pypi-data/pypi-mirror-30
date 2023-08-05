from os import getcwd, chdir, chmod, walk, \
    readlink, listdir, utime, stat as osstat
from os.path import expanduser, islink, \
    isfile, isdir, abspath, join as pjoin
from shutil import copy2
import inspect
from stat import S_ISSOCK as _ISSOCK
from configparser import ConfigParser as _ConfPars
from json import load as _jsonload

from system.random import randin

def absrelpath(path, base=None):
	base = base if base else getcwd()
	path = path.strip("'")
	path = path.strip('"')
	if path.startswith('~'):
		path = expanduser(path)
	if islink(path):
		path = readlink(path)
	if '..' in path or not path.startswith('/'):
		pwd = getcwd()
		chdir(base)
		path = abspath(path)
		chdir(pwd)
	return path.rstrip('/')

def realpaths(pathlist, base=None):
	base = base if base else getcwd()
	paths = []
	for path in pathlist:
		if isinstance(path, (list, tuple)):
			#print('list/tuple')
			for pat in path:
				paths = [absrelpath(p, base) for p in path]
		elif isinstance(path, str):
			if ' ' in path:
				#print('liststring')
				paths = [absrelpath(p.strip(), base) for p in path.strip('[]').split(',')]
				break
			else:
				#print('string', path)
				paths.append(absrelpath(path, base))
	return paths

def confpaths(paths, conf, base=''):
	return list(set([pjoin(expanduser('~'), path[2:], conf) \
        for path in paths if path.startswith('~/') and \
        isfile(pjoin(expanduser('~'), path[2:], conf))] + \
        [pjoin(base, path[2:], conf) for path in \
        paths if path.startswith('./') and \
        isfile(pjoin(base, path[2:], conf))] + \
        [pjoin(base, path, conf) for path in paths if not \
        path.startswith('/') and not path.startswith('.') and \
        isfile(pjoin(base, path, conf))] + \
        [pjoin(path, conf) for path in paths if path.startswith('/') and \
        isfile(pjoin(path, conf))]))

def confdats(*confs):
	cfg = _ConfPars()
	confdats = {}
	for conf in confs:
		cfg.read(conf)
		for section in cfg.sections():
			confdats[section] = dict(cfg[section])
	return confdats

def jconfdats(*confs):
	confdats = {}
	for conf in confs:
		with open(conf, 'r') as stream:
			for (key, val) in _jsonload(stream).items():
				confdats[key] = val
	return confdats

def unsorted(files):
	rands = []
	for i in range(0, len(files)):
		newrand = randin(len(files))
		if newrand in rands:
			continue
		yield files[newrand]

def filetime(trg):
	"""local file-timestamp method"""
	return int(osstat(trg).st_mtime), int(osstat(trg).st_atime)

def setfiletime(trg, mtime=None, atime=None):
	"""local file-timestamp set method"""
	mt, at = filetime(trg)
	if mtime and not atime:
		atime = at
	elif atime and not mtime:
		mtime = mt
	utime(trg, (at, mt))

def filerotate(lfile, count=1):
	for i in reversed(range(0, int(count))):
		old = lfile if i == 0 else '%s.%d'%(lfile, i)
		new = '%s.%d'%(lfile, int(i+1))
		try:
			mt, at = filetime(old)
		except FileNotFoundError:
			continue
		copy2(old, new)
		setfiletime(new, mt, at)

def filesiter(folder, random=False):
	for (d, _, fs) in walk(absrelpath(folder)):
		orderd = sorted if not random else unsorted
		for f in orderd(fs):
			yield pjoin(d, f)

def findupperdir(path, name):
	while len(path.split('/')) > 1:
		trg = pjoin(path, name)
		if isdir(trg):
			return trg
		return findupperdir('/'.join(p for p in path.split('/')[:-1]), name)
