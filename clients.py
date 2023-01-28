#!/usr/bin/env python3

import sys, collections
from omada import Omada

FIELDDEF = collections.OrderedDict([
	('name',        ('USERNAME',     20)),
	('ip',          ('IP ADDRESS',   16)),
	('active',      ('STATUS',       12)),
	('networkName', ('SSID/NETWORK', 16)),
	('port',        ('AP/PORT',      16)),
	('activity',    ('ACTIVITY',     12)),
	('trafficDown', ('DOWNLOAD',     10)),
	('trafficUp',   ('UPLOAD',       10)),
	('uptime',      ('UPTIME',       16)),
])

def format_status( active ):
	return 'CONNECTED' if active else '--'

def format_port( switch, port ):
	return f'{switch} Port {port}'

def format_size( size, suffix='B' ):
	for unit in ['K','M','G','T','P','E','Z']:
		size /= 1000.0
		if abs( size ) < 1000.0:
			return f'{size:.1f} {unit}{suffix}'
	return f'{size:.1f} Y{suffix}'

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

def print_client( client ):

	for key in client:

		if key == 'active':
			client[key] = format_status( client['active'] )

		elif key == 'port':
			client[key] = format_port( client['switchName'], client['port'] )

		elif key == 'activity':
			client[key] = format_size( client['activity'], 'B/s' )

		elif key == 'trafficDown':
			client[key] = format_size( client['trafficDown'], 'B' )

		elif key == 'trafficUp':
			client[key] = format_size( client['trafficUp'], 'B' )

		elif key == 'uptime':
			client[key] = format_time( client['uptime'] )

	if client['connectDevType'] == 'ap':
		client['networkName'] = client['ssid']
		client['port'] = client['apName']

	for key in FIELDDEF:

		text = client[key] if key in client else '--'
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

	for client in omada.getSiteClients():
		print_client( client )

	omada.logout()

if __name__ == '__main__':
	main()
