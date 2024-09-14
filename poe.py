#!/usr/bin/env python3

import sys, collections
from omada import Omada

def format_poe(poe):
	if poe == 0:
		return 'Disabled'
	elif poe == 1:
		return 'Enabled'
	elif poe == 2:
		return "Keep the Device's Settings"

def main():
	if len(sys.argv) > 2 and sys.argv[2] not in ("0", "1", "2"):
		print( f"usage: {sys.argv[0]} [profile name] [0|1|2]" )
		return

	omada = Omada('omada.cfg')
	omada.login()

	if len(sys.argv) > 2:
		profileId = omada.getProfileId(sys.argv[1])
		settings = omada.getProfileSettings(profileId)
		settings['poe'] = sys.argv[2]
		omada.setProfileSettings(profileId, settings)

		settings = omada.getProfileSettings(profileId)
		print( f"Changed the poe setting for profile {settings['name']} to {format_poe(settings['poe'])}.")
		
	omada.logout()

if __name__ == '__main__':
	main()
