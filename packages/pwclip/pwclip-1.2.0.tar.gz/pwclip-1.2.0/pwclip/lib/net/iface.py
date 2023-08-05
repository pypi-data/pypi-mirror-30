#!/usr/bin/env python3

from re import sub

from os import listdir

from os.path import isfile

import sys

import curses

from time import sleep

from netifaces import ifaddresses, AF_INET, AF_INET6

from net.addr import addrmask

from colortext import blu, yel, vio

from executor.executor import command as cmd

def ifaces(netdir='/sys/class/net'):
	return [d.strip() for d in listdir(netdir)]

def ifaddrs(iface, ipv4=True, ipv6=True):
	ip4s = []
	ip6s = []
	if ipv4:
		try:
			for ip4 in ifaddresses(iface)[AF_INET]:
				ip4s.append(ip4)
		except KeyError:
			pass
	if ipv6:
		try:
			for ip6 in ifaddresses(iface)[AF_INET6]:
				if 'addr' in ip6.keys() and '%' in ip6['addr']:
					ip6['addr'] = ip6['addr'].split('%')[0]
				ip6s.append(ip6)
		except KeyError:
			pass
	if ip4s and ip6s:
		return {'ipv4':ip4s, 'ipv6':ip6s}
	elif ip4s:
		return {'ipv4':ip4s}
	elif ip6s:
		return {'ipv6':ip6s}

def _rxtx(iface):
	out = cmd.stdo('/sbin/ifconfig %s'%iface)
	if not out: raise RuntimeError('could not get ifconfig output')
	for l in out.split('\n'):
		if 'RX packets ' in l:
			rb = l.strip().split('bytes ')[1].split(' ')[0]
		elif 'TX packets ' in l:
			tb = l.strip().split('bytes ')[1].split(' ')[0]
	return int(rb), int(tb)

def _xbytes(iface):
	ru, tu = ' b/s', ' b/s'
	srb, stb = _rxtx(iface)
	sleep(0.99)
	nrb, ntb = _rxtx(iface)
	rb, tb = int(nrb-srb), int(ntb-stb)
	if rb > 1024:
		ru = 'Kb/s'
		rb = int(rb/1024)
	if tb > 1024:
		tu = 'Kb/s'
		tb = int(tb/1024)
	if rb > 1024:
		ru = 'Mb/s'
		rb = int(rb/1024)
	if tb > 1024:
		tu = 'Mb/s'
		tb = int(tb/1024)
	if rb > 1024:
		ru = 'Gb/s'
		rb = int(rb/1024)
	if tb > 1024:
		tu = 'Gb/s'
		tb = int(tb/1024)
	return '  %03s %s  U%s %s %sD  %03s %s'%(
        tb if tb else '', vio(tu), blu('>>'),
        yel(iface if iface != 'lo' else ' lo '),
        blu('<<'), rb if rb else '', vio(ru))


def ifthrough(ifaces):
	print(blu('monitoring network throughput...'))
	sleep(1.5)
	stdio = curses.initscr()
	stdio.nodelay(1)
	curses.noecho()
	try:
		while True:
			print('\033c\n\r%s\r%s'%(
                '\r\n\n'.join(_xbytes(i) for i in ifaces if i),
                blu('\n\n     ( press any key to exit )\r')))
			if stdio.getch() != -1:
				break
	except KeyboardInterrupt:
		pass
	finally:
		curses.nocbreak()
		curses.echo()
		curses.endwin()
		print('\033c%s'%blu('monitor stopped by user input'))


def anyifconfd():
	confdifs = []
	for iface in ifaces():
		if iface == 'lo':
			continue
		ipaddrs = ifaddrs(iface)
		if ipaddrs:
			for ipv in ipaddrs:
				for ips in ipaddrs[ipv]:
					if 'addr' in ips.keys() and not iface in confdifs:
						confdifs.append(iface)
						break
	return confdifs

def isconfd(iface):
	if iface in anyifconfd():
		return True

def haslink(iface, netdir='/sys/class/net'):
	linkfile = netdir+'/'+iface+'/carrier'
	if isfile(linkfile):
		try:
			with open(linkfile, 'r') as f:
				link = f.read()
			if link.strip() == '1':
				return True
		except OSError:
			return False

def isup(iface, netdir='/sys/class/net'):
	statefile = netdir+'/'+iface+'/operstate'
	state = None
	if isfile(statefile):
		try:
			with open(statefile, 'r') as f:
				state = f.read()
		except:
			state = False
		finally:
			if state:
				if state.strip() == 'up':
					return True


def iftype(iface, netdir='/sys/class/net'):
	infofile = '%s/%s/uevent'%(netdir, iface)
	if isfile(infofile):
		with open(infofile, 'r') as f:
			ifinfo = f.readlines()
		for line in ifinfo.split('\n'):
			if 'DEVTYPE' in line:
				return str(line.split('=')[1]).strip()
			elif 'INTERFACE' in line:
				return str(line.split('=')[1][:-1]).strip()
	return re.sub(r'\d$', '', iface)

def currentnets():
	for iface in anyifconfd():
		ifips = ifaddrs(iface)
		if ifips and 'ipv4' in ifips.keys():
			for ips in ifips['ipv4']:
				if 'addr' in ips:
					netaddress, netbits = addrmask(
                        ips['addr'], ips['netmask'])
					yield '%s/%s'%(netaddress, netbits)
