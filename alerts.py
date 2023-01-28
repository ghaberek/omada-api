#!/usr/bin/env python3

import sys, time, re, collections
from omada import Omada

FIELDDEF = collections.OrderedDict([
	('content',('CONTENT',72)),
	('time',   ('TIME',   24)),
])

def format_date( date ):
	return time.strftime('%b %e %Y %I:%M:%S %p', time.localtime(date // 1000))

def print_header():

	if sys.stdout.isatty():
		sys.stdout.write( '\33[1m' )

	for key in FIELDDEF:
		text,width = FIELDDEF[key]
		sys.stdout.write( text.ljust(abs(width)) )

	if sys.stdout.isatty():
		sys.stdout.write( '\33[0m' )

	sys.stdout.write( '\n' )

def print_alert( alert ):

	for key in alert:

		if key == 'content':
			match = re.search( r'\[([a-z]+):([0-9A-F\-]+)\]', alert[key] )
			if match:
				tag = str( match.group(1) )
				mac = str( match.group(2) )
				type = 'clientNames' if tag == 'client' else 'deviceNames'
				name = '[' + alert[type][mac] + ']'
				alert[key] = alert[key].replace( match.group(0), name )

		elif key == 'time':
			alert[key] = format_date( alert[key] )

	for key in FIELDDEF:

		text = alert[key].strip() if key in alert else '--'
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

	for alert in omada.getSiteAlerts():
		print_alert( alert )

	omada.logout()

if __name__ == '__main__':
	main()
