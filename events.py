#!/usr/bin/env python3

import sys, time, re, collections
from omada import Omada

FIELDDEF = collections.OrderedDict([
	('content',('CONTENT',92)),
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

def print_event( event ):

	for key in event:

		if key == 'content':
			match = re.search( r'\[([a-z]+):([0-9A-F\-]+)\]', event[key] )
			while match:
				tag = str( match.group(1) )
				mac = str( match.group(2) )
				type = 'clientNames' if tag == 'client' else 'deviceNames'
				name = '[' + event[type][mac] + ']'
				event[key] = event[key].replace( match.group(0), name )
				match = re.search( r'\[([a-z]+):([0-9A-F\-]+)\]', event[key] )

		elif key == 'time':
			event[key] = format_date( event[key] )

	for key in FIELDDEF:

		text = event[key].strip() if key in event else '--'
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

	count = 1
	for event in omada.getSiteEvents():
		print_event( event )
		if count == 50:
			break
		count += 1

	omada.logout()

if __name__ == '__main__':
	main()
