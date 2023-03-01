#!/usr/bin/env python3

import sys
from omada import Omada

def main():
	if len(sys.argv) > 4 or len(sys.argv) < 4:
		print( f"usage:" )
		print( f"   {sys.argv[0]} JKS jks_path storepass" )
		print( f"   {sys.argv[0]} PFX pfx_path storepass" )
		print( f"   {sys.argv[0]} PEM cert_path key_path" )
		return

	omada = Omada()
	omada.login()
	if sys.argv[1] == "JKS":
		omada.setControllerJksCertificate(jks_path=sys.argv[2], password=sys.argv[3])
	elif sys.argv[1] == "PFX":
		omada.setControllerPfxCertificate(pfx_path=sys.argv[2], password=sys.argv[3])
	elif sys.argv[1] == "PEM":
		omada.setControllerPemCertificate(cert_path=sys.argv[2], key_path=sys.argv[3])
	else:
		raise Exception("Unsupported cert type: " + sys.argv[1])

	omada.reboot()

if __name__ == '__main__':
	main()
