#!/usr/bin/env python3

import sys, collections
from omada import Omada

FIELDDEF = collections.OrderedDict([
	('name',      ('NAME',       16)),
	('ip',        ('IP ADDRESS', 16)),
	('status',    ('STATUS',     12)),
	('showModel', ('MODEL',      24)),
	('version',   ('VERSION',    12)),
	('uptime',    ('UPTIME',     16)),
])

def format_time( time ):
	d = time // (3600 * 24)
	h = time // 3600 % 24
	m = time % 3600 // 60
	s = time % 3600 % 60
	if d > 0: return f'{d}d {h}:{m:02d}:{s:02d}'
	if h > 0: return f'{h}:{m:02d}:{s:02d}'
	if m > 0: return f'{m:02d}:{s:02d}'
	if s > 0: return f'{s:02d}'
	return '--'

def print_header():

	if sys.stdout.isatty():
		sys.stdout.write( '\33[1m' )

	for key in FIELDDEF:
		text,width = FIELDDEF[key]
		sys.stdout.write( text.ljust(abs(width)) )

	if sys.stdout.isatty():
		sys.stdout.write( '\33[0m' )

	sys.stdout.write( '\n' )

def print_device( device ):

	for key in device:

		if key == 'status':
			device[key] = 'CONNECTED' if device['status'] else '--'

		elif key == 'uptime':
			device[key] = format_time( device['uptimeLong'] )

	for key in FIELDDEF:

		text = device[key] if key in device else '--'
		if not isinstance(text,str): text = str(text)

		width = FIELDDEF[key][1]

		if len(text) >= abs(width):
			text = text[0:abs(width)-4] + '... '
		elif width > 0:
			text = text.ljust(abs(width))
		else:
			text = text.rjust(abs(width)-1)

		sys.stdout.write( text )

	sys.stdout.write( '\n' )

def main():
	omada = Omada()
	omada.login()

	print_header()

	for device in omada.getSiteDevices():
		print_device( device )

	omada.logout()

if __name__ == '__main__':
	main()
