#!/usr/bin/env python3

import sys
from omada import Omada

def main():
	if len(sys.argv) < 2 or (len(sys.argv) > 1 and sys.argv[1] not in ('enable','disable')):
		print( f"usage: {sys.argv[0]} [enable|disable]" )
		return

	omada = Omada()
	omada.login()

	devices = omada.getSiteDevices()
	if len(devices) > 0:
		gateway = next((device for device in devices if device['type'] == 'gateway'), None)
		print(f"Selected gateway: {gateway}")
		if gateway:
			mac = gateway['mac']
		else:
			print( 'No gateway device found' )
			return
		
		omada.setInternetStatus(mac=mac, port_id=1, enable=sys.argv[1] == 'enable')
		gateway = omada.getGatewayDevice(mac=mac)
		print( f'Updated gateway: {gateway}' )

	omada.logout()

if __name__ == '__main__':
	main()
