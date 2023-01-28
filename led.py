#!/usr/bin/env python3

import sys
from omada import Omada

def main():
	if len(sys.argv) > 1 and sys.argv[1] not in ('on','off'):
		print( f"usage: {sys.argv[0]} [on|off]" )
		return

	omada = Omada()
	omada.login()

	settings = omada.getSiteSettings()

	if len(sys.argv) > 1:
		settings['led']['enable'] = (sys.argv[1] == 'on')
		omada.setSiteSettings(settings)
		settings = omada.getSiteSettings()

	print( 'led: on' if settings['led']['enable'] else 'led: off' )

	omada.logout()

if __name__ == '__main__':
	main()
