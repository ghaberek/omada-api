
import json
import urllib3
import warnings
from configparser import ConfigParser
from datetime import datetime
from requests import Session

def timestamp():
	return int( datetime.utcnow().timestamp() * 1000 )

class Omada:

	def __init__(self, config, baseurl=None, site='Default', verify=True):
		
		if config is not None:
			parser = ConfigParser()
			parser.read( config )
			if 'omada' in parser:
				baseurl  = parser['omada'].get('baseurl')
				verify   = parser['omada'].getboolean('verify')
				site     = parser['omada'].get('site')
				username = parser['omada'].get('username')
				password = parser['omada'].get('password')
		
		if verify == False:
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		
		session = Session()
		session.verify = verify
		
		self.baseurl = baseurl
		self.site = site
		self.username = username
		self.password = password
		self.session = session
		self.token = None

	def login(self, username=None, password=None):
		if username is None: username = self.username
		if password is None: password = self.password
		
		response = self.session.post( f'{self.baseurl}/api/v2/login', json={'username':username,'password':password} )
		json = response.json()
		
		if json['errorCode'] == 0:
			self.username = username
			self.password = password
			self.token = json['result']['token']
			return True
		
		return None

	def logout(self):
		response = self.session.post( f'{self.baseurl}/api/v2/logout', params={'token':self.token} )
		json = response.json()
		
		if json['errorCode'] == 0:
			self.token = None
			return True
		
		return None

	def getLoginStatus(self):
		response = self.session.get( f'{self.baseurl}/api/v2/loginStatus', params={'token':self.token,'_':timestamp()} )
		json = response.json()
		
		if json['errorCode'] == 0:
			return json['result']['login']
		
		return None

	def getCurrentUser(self):
		response = self.session.get( f'{self.baseurl}/api/v2/users/current', params={'token':self.token,'_':timestamp()} )
		json = response.json()
		
		if json['errorCode'] == 0:
			return json['result']['id']
		
		return None

	def getCurrentSite(self):
		response = self.session.get( f'{self.baseurl}/api/v2/users/current', params={'token':self.token,'_':timestamp()} )
		json = response.json()
		
		if json['errorCode'] == 0:
			return json['result']['privilege']['lastVisited']
		
		return None

	def getSiteSettings(self, site=None):
		if site is None: site = self.site
		
		response = self.session.get( f'{self.baseurl}/api/v2/sites/{site}/setting', params={'token':self.token,'_':timestamp()} )
		json = response.json()
		
		if json['errorCode'] == 0:
			# work-around for error when sending PATCH for site settings (see below)
			if 'beaconControl' in json['result']: del json['result']['beaconControl']
			return json['result']
		
		return None

	def setSiteSettings(self, settings, site=None):
		if site is None: site = self.site
		
		# not sure why but setting 'beaconControl' here does not work, returns {'errorCode': -1001}
		if 'beaconControl' in settings:
			warnings.warn( "settings['beaconControl'] was removed as it causes an error", stacklevel=2 )
			del settings['beaconControl']
		
		response = self.session.patch( f'{self.baseurl}/api/v2/sites/{site}/setting', params={'token':self.token}, json=settings )
		json = response.json()
		
		if json['errorCode'] == 0:
			return True
		
		return None

