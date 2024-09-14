#!/usr/bin/env python3

import sys, collections
from omada import Omada

FIELDDEF = collections.OrderedDict([
	('id',              ('ID',                30)),
	('name',            ('NAME',              30)),
	('poe',             ('POE',               30)),
	('nativeNetworkId', ('Native Network ID', 30)),
])

def format_poe (poe):
	if poe == 0:
		return 'Disabled'
	elif poe == 1:
		return 'Enabled'
	elif poe == 2:
		return 'Keep the device settings'
	else:
		return 'Unknown'


def print_header():

	if sys.stdout.isatty():
		sys.stdout.write( '\33[1m' )

	for key in FIELDDEF:
		text,width = FIELDDEF[key]
		sys.stdout.write( text.ljust(abs(width)) )

	if sys.stdout.isatty():
		sys.stdout.write( '\33[0m' )

	sys.stdout.write( '\n' )

def print_profile ( profile ):
	for key in profile:
		if key == 'poe':
			profile[key] = format_poe( profile['poe'])

	for key in FIELDDEF:
		text = profile[key] if key in profile else '--'
		if not isinstance(text, str): text = str(text)

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
	omada = Omada('omada.cfg')
	omada.login()

	print_header()

	profiles = omada.getProfiles()

	for profile in profiles:
		print_profile( profile )

	omada.logout()

if __name__ == '__main__':
	main()
