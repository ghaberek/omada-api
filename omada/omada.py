
import os
import json
import requests
import urllib3
import warnings
import http.client
import logging
from configparser import ConfigParser
from datetime import datetime
from enum import Enum
from requests.cookies import RequestsCookieJar

#define Logger for class-wide usage
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

##
## Omada API calls expect a timestamp in milliseconds.
##
def timestamp():
	return int( datetime.utcnow().timestamp() * 1000 )

##
## Display errorCode and optional message returned from Omada API.
##
class OmadaError(Exception):

	def __init__(self, json):
		self.errorCode = 0
		self.msg = None

		if json is None:
			raise TypeError('json cannot be None')

		if 'errorCode' in json:
			self.errorCode = int( json['errorCode'] )

		if 'msg' in json:
			self.msg = '"' + json['msg'] + '"'

	def __str__(self):
		return f'errorCode={self.errorCode}, msg={self.msg}'

##
## The main Omada API class.
##
class Omada:

	##
	## Default API
	##
	ApiPath = '/api/v2'

	##
	## Group types
	##
	class GroupType(Enum):
		IPGroup     = 0 # "IP Group"
		IPPortGroup = 1 # "IP-Port Group"
		MACGroup    = 2 # "MAC Group"

	##
	## Alert and event levels
	##
	class LevelFilter(Enum):
		Error       = 0
		Warning     = 1
		Information = 2

	##
	## Alert and event modules
	##
	class ModuleFilter(Enum):
		Operation = 0
		System    = 1
		Device    = 2
		Client    = 3

	##
	## Initialize a new Omada API instance.
	##
	def __init__(self, config='omada.cfg', baseurl=None, site='Default', verify=True, warnings=True, verbose=False):

		self.config = None
		self.loginResult = None
		self.currentPageSize = 10
		self.currentUser = {}
		self.apiPath = Omada.ApiPath
		self.omadacId = ''

		if baseurl is not None:
			# use the provided configuration
			self.baseurl  = baseurl
			self.site     = site
			self.verify   = verify
			self.warnings = warnings
			self.verbose  = verbose
		elif os.path.isfile( config ):
			# read from configuration file
			self.config = ConfigParser()
			try:
				self.config.read( config )
				self.baseurl  = self.config['omada'].get('baseurl')
				self.site     = self.config['omada'].get('site', 'Default')
				self.verify   = self.config['omada'].getboolean('verify', True)
				self.warnings = self.config['omada'].getboolean('warnings', True)
				self.verbose  = self.config['omada'].getboolean('verbose', False)
			except:
				raise
		else:
			# could not find configuration
			raise FileNotFoundError(config)

		# set up requests session and cookies
		self.session = requests.Session()
		self.session.cookies = RequestsCookieJar()
		self.session.verify = self.verify

		# hide warnings about insecure SSL requests
		if self.verify == False and self.warnings == False:
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

		# enable verbose output
		if self.verbose:
			# set debug level in http.client
			http.client.HTTPConnection.debuglevel = 1
			# initialize logger
			logging.basicConfig()
			logging.getLogger().setLevel(logging.DEBUG)
			# configure logging for requests
			logger.setLevel(logging.DEBUG)
			logger.propagate = True

	##
	## Build a URL for the provided path.
	##
	def __buildUrl(self, path):
		return self.baseurl + self.omadacId + self.apiPath + path

	##
	## Look up a site key given the name.
	##
	def __findKey(self, name=None):

		# Use the stored site if not provided.
		if name is None: name = self.site

		# Look for the site in the privilege list.
		for site in self.currentUser['privilege']['sites']:
			if site['name'] == name: return site['key']

		raise PermissionError(f'current user does not have privilege to site "{name}"')

	##
	## Perform a GET request and return the result.
	##
	def __get(self, path, params={}, data=None, json=None):

		if self.loginResult is None:
			raise ConnectionError('not logged in')

		if not isinstance(params, dict):
			raise TypeError('params must be a dictionary')

		response = self.session.get( self.__buildUrl(path), params=params, data=data, json=json, headers=self.session.headers )
		response.raise_for_status()

		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None

		raise OmadaError(json)

	##
	## Perform a POST request and return the result.
	##
	def __post(self, path, params={}, data=None, files=None, json=None):

		if self.loginResult is None:
			raise ConnectionError('not logged in')

		if not isinstance(params, dict):
			raise TypeError('params must be a dictionary')

		params['_'] = timestamp()
		params['token'] = self.loginResult['token']
		response = self.session.post( self.__buildUrl(path), params=params, data=data, files=files, json=json )
		response.raise_for_status()

		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None

		raise OmadaError(json)

	##
	## Perform a PATCH request and return the result.
	##
	def __patch(self, path, params={}, data=None, json=None):

		if self.loginResult is None:
			raise ConnectionError('not logged in')

		if not isinstance(params, dict):
			raise TypeError('params must be a dictionary')

		params['_'] = timestamp()
		params['token'] = self.loginResult['token']

		response = self.session.patch( self.__buildUrl(path), params=params, data=data, json=json )
		response.raise_for_status()

		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None

		raise OmadaError(json)

	##
	## Return True if a result contains data.
	##
	def __hasData(self, result):
		return (result is not None) and ('data' in result) and (len(result['data']) > 0)

	##
	## Perform a paged GET request and return the result.
	##
	def __getPaged(self, path, params={}, data=None, json=None):

		if self.loginResult is None:
			raise ConnectionError('not logged in')

		if not isinstance(params, dict):
			raise TypeError('params must be a dictionary')

		params['_'] = timestamp()
		params['token'] = self.loginResult['token']

		if 'currentPage' not in params:
			params['currentPage'] = 1

		if 'currentPageSize' not in params:
			params['currentPageSize'] = self.currentPageSize

		response = self.session.get( self.__buildUrl(path), params=params, data=data, json=json )
		response.raise_for_status()

		json = response.json()
		if json['errorCode'] == 0:
			json['result']['path'] = path
			json['result']['params'] = params
			return json['result']

		raise OmadaError(json)

	##
	## Returns the next page of data if more is available.
	##
	def __nextPage(self, result):

		if 'path' in result:
			path = result['path']
			del result['path']
		else:
			return None

		if 'params' in result:
			params = result['params']
			del result['params']
		else:
			return None

		totalRows   = int( result['totalRows'] )
		currentPage = int( result['currentPage'] )
		currentSize = int( result['currentSize'] )
		dataLength  = len( result['data'] )

		if dataLength + (currentPage-1)*currentSize >= totalRows:
			return None

		params['currentPage'] = currentPage + 1
		return self.__getPaged( path, params )

	##
	## Perform a GET request and yield the results.
	##
	def __geterator(self, path, params={}, data=None, json=None):
		result = self.__getPaged( path, params, data, json )
		while self.__hasData( result ):
			for item in result['data']: yield item
			result = self.__nextPage( result )

	##
	## Issue a warning if warnings are enabled.
	##
	def __warn(self, message, category=None, stacklevel=1, source=None):
		if self.warnings: warnings.warn( message, category, stacklevel, source )

	##
	## Get OmadacId to prefix request. (Required for version 5.)
	##
	def getApiInfo(self):

		# This uses a different path, so perform request manually.
		response = self.session.get( self.baseurl + '/api/info' )
		response.raise_for_status()

		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None

		raise OmadaError(json)

	##
	## Log in with the provided credentials and return the result.
	##
	def login(self, username=None, password=None):

		# Only try to log in if we're not already logged in.
		if self.loginResult is None:

			# Fetch the API info from the controller. (Does not require login.)
			apiInfo = self.getApiInfo()

			# Store the omadacId value. (Required by version 5.)
			if 'omadacId' in apiInfo:
				self.omadacId = '/' + apiInfo['omadacId']

			# Get the username and password if not specified.
			if username is None and password is None:
				if self.config is None:
					raise TypeError('username and password cannot be None')
				try:
					username = self.config['omada'].get('username')
					password = self.config['omada'].get('password')
				except:
					raise

			# Perform the login request manually.
			response = self.session.post( self.__buildUrl('/login'), json={'username':username,'password':password} )
			response.raise_for_status()

			# Get the login response.
			json = response.json()
			if json['errorCode'] != 0:
				raise OmadaError(json)

			# Store the login result.
			self.loginResult = json['result']

			# Store CSRF token header.
			self.session.headers.update({
				"Csrf-Token": self.loginResult['token']
			})

			# Get the current user info.
			self.currentUser = self.getCurrentUser()

		return self.loginResult

	##
	## Log out of the current session. Return value is always None.
	##
	def logout(self):

		result = None

		# Only try to log out if we're already logged in.
		if self.loginResult is not None:
			# Send the logout request.
			result = self.__post( '/logout' )
			# Clear the stored result.
			self.loginResult = None

		return result

	##
	## Returns the current login status.
	##
	def getLoginStatus(self):
		return self.__get( '/loginStatus' )

	##
	## Returns the current user information.
	##
	def getCurrentUser(self):
		return self.__get( '/users/current' )

	##
	## Returns the list of groups for the given site.
	##
	def getSiteGroups(self, site=None, type=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting/profiles/groups' + (f'/{type}' if type else '') )

	##
	## Returns the list of portal candidates for the given site.
	##
	## This is the "SSID & Network" list on Settings > Authentication > Portal > Basic Info.
	##
	def getPortalCandidates(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting/portal/candidates' )

	##
	## Returns the list of RADIUS profiles for the given site.
	##
	def getRadiusProfiles(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting/radiusProfiles' )

	##
	## Returns the list of scenarios.
	##
	def getScenarios(self):
		return self.__get( '/scenarios' )

	##
	## Returns the list of all sites.
	##
	def getSites(self):
		return self.__geterator( f'/sites' )

	##
	## Returns the list of devices for given site.
	##
	def getSiteDevices(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/devices' )

	##
	## Returns the list of active clients for given site.
	##
	def getSiteClients(self, site=None):
		return self.__geterator( f'/sites/{self.__findKey(site)}/clients', params={'filters.active':'true'} )

	##
	## Returns the list of alerts for given site.
	##
	def getSiteAlerts(self, site=None, archived=False, level=None, module=None, searchKey=None):

		params = {'filters.archived': 'true' if archived else 'false'}

		if level is not None:
			if level not in ValidLevelFilters:
				raise TypeError('invalid level filter')
			params['filters.level'] = level

		if module is not None:
			if level not in ValidModuleFilters:
				raise TypeError('invalid module filter')
			params['filters.module'] = module

		if searchKey is not None:
			params['searchKey'] = searchKey

		return self.__geterator( f'/sites/{self.__findKey(site)}/alerts', params=params )

	##
	## Returns the list of events for given site.
	##
	def getSiteEvents(self, site=None, level=None, module=None, searchKey=None):

		params = {}

		if level is not None:
			if level not in ValidLevelFilters:
				raise TypeError('invalid level filter')
			params['filters.level'] = level

		if module is not None:
			if module not in ValidModuleFilters:
				raise TypeError('invalid module filter')
			params['filters.module'] = module

		if searchKey is not None:
			params['searchKey'] = searchKey

		return self.__geterator( f'/sites/{self.__findKey(site)}/events', params=params )

	##
	## Returns the notification settings for given site.
	##
	def getSiteNotifications(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/notification' )

	##
	## Returns the list of settings for the given site.
	##
	def getSiteSettings(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting' )

	##
	## Push back the settings for the site.
	##
	def setSiteSettings(self, settings, site=None):
		return self.__patch( f'/sites/{self.__findKey(site)}/setting', json=settings )

	##
	## Returns the list of settings for the controller.
	##
	def getControllerSettings(self):
		return self.__get( f'/controller/setting' )

	##
	## Push back the settings for the controller.
	##
	def setControllerSettings(self, settings):
		return self.__patch( f'/controller/setting', json=settings )


	def setControllerJksCertificate(self, jks_path, password):
		return self.__setControllerCertificate(cert_type="JKS",
						       cert_path=jks_path,
						       key_password=password)


	def setControllerPfxCertificate(self, pfx_path, password):
		return self.__setControllerCertificate(cert_type="PFX",
						       cert_path=pfx_path,
						       key_password=password)


	def setControllerPemCertificate(self, cert_path, key_path):
		return self.__setControllerCertificate(cert_type="PEM",
						       cert_path=cert_path,
						       key_path=key_path)


	def __uploadFile(self, src_path, dest_path, data, content_type="application/octet-stream"):
		src_name = os.path.basename(src_path)
		with open(src_path, 'rb') as src_file:
			result = self.__post(f'/files/{dest_path}',
					     files={'file': (src_name,
							     src_file,
							     content_type),
						    'data': (None, json.dumps(data))})
	
	##
	## Set new certificate for the controller
	##
	def __setControllerCertificate(self, cert_type, cert_path, key_path=None, key_password=None):
		r_cert = self.__uploadFile(cert_path,
					   'controller/certificate',
					   {"cerName": os.path.basename(cert_path)})
		if key_path:
			r_key = self.__uploadFile(key_path,
						  'controller/key',
						  {"keyName": os.path.basename(key_path)})

		# re-upload same settings to force cert file validation
		settings = self.getControllerSettings()
		cert_settings = settings['certificate']
		cert_settings['cerType'] = cert_type
		cert_settings['enable'] = True
		if key_password:
			cert_settings['keyPassword'] = key_password
		else:
			cert_settings.pop('keyPassword', None)
		if not key_path:
			# Delete PEM key file details if they exist
			cert_settings.pop('keyId', None)
			cert_settings.pop('keyName', None)
		return self.setControllerSettings(settings)
			

	def reboot(self):
		return self.__post('/cmd/reboot')
	
	
	##
	## Returns the list of timerange profiles for the given site.
	##
	def getTimeRanges(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting/profiles/timeranges' )

	##
	## Returns the list of wireless network groups.
	##
	## This is the "WLAN Group" list on Settings > Wireless Networks.
	##
	def getWirelessGroups(self, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting/wlans' )

	##
	## Returns the list of wireless networks for the given group.
	##
	## This is the main SSID list on Settings > Wireless Networks.
	##
	def getWirelessNetworks(self, group, site=None):
		return self.__get( f'/sites/{self.__findKey(site)}/setting/wlans/{group}/ssids' )
