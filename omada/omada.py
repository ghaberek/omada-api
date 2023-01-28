# -*- coding: future_fstrings -*-

import os
import requests
import urllib3
import warnings
import http.client
import logging
from configparser import ConfigParser
from datetime import datetime

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
			self.errorCode = json['errorCode']
		
		if 'msg' in json:
			self.msg = '"' + json['msg'] + '"'

	def __str__(self):
		return f"errorCode={self.errorCode}, msg={self.msg}"

##
## The main Omada API class.
##
class Omada:

	##
	## Initialize a new Omada API instance.
	##
	def __init__(self, config='omada.cfg', baseurl=None, site='Default', verify=True, warnings=True, verbose=False):
		
		self.config = None
		self.token  = None
		self.currentPageSize = 10
		self.currentUser = {}
		self.omadacId = None
		
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
		
		self.session = requests.Session()
		jar = RequestsCookieJar()
		self.session.cookies = jar

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
	## Current API path.
	##
	ApiPath = '/api/v2'

	##
	## Build a URL for the provided path.
	##
	def url_for(self, path):
		baseurl = self.baseurl + "/"
		if self.omadacId is not None:
			baseurl = baseurl + self.omadacId
		return baseurl + Omada.ApiPath + path
		
	##
	## Look up a site key given the name.
	##
	def site_key(self, name):
		if name is None:
			name = self.site
		for site in self.currentUser['privilege']['sites']:
			if site['name'] == name: return site['key']
		return name

	##
	## Return True if a result contains data.
	##
	def hasData(self, result):
		return (result is not None) and ('data' in result) and (len(result['data']) > 0)

	##
	## Returns the next page of data if more is available.
	##
	def nextPage(self, result):
		
		if 'path' not in result:
			return None
		
		path = result['path']
		del result['path']
		
		if 'params' not in result:
			return None
		
		params = result['params']
		del result['params']
		
		totalRows   = int( result['totalRows'] )
		currentPage = int( result['currentPage'] )
		currentSize = int( result['currentSize'] )
		dataLength  = len( result['data'] )
		
		if dataLength + (currentPage-1)*currentSize >= totalRows:
			return None
		
		params['currentPage'] = currentPage + 1
		return self.get_paged( path, params )

	##
	## Perform a GET request and return the result.
	##
	def get(self, path, params={}, data=None, json=None):

		headers = {}
		headers["Csrf-Token"] = self.token
		self.session.headers.update(headers)

		response = self.session.get( self.url_for(path), params=params, data=data, json=json , headers=self.session.headers)
		response.raise_for_status()
		
		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None
		
		raise OmadaError(json)

	##
	## Perform a paged GET request and return the result.
	##
	def get_paged(self, path, params={}, data=None, json=None):
		
		params['_'] = timestamp()
		params['token'] = self.token
		
		if 'currentPage' not in params:
			params['currentPage'] = 1
		
		if 'currentPageSize' not in params:
			params['currentPageSize'] = self.currentPageSize
		
		response = self.session.get( self.url_for(path), params=params, data=data, json=json )
		response.raise_for_status()
		
		json = response.json()
		if json['errorCode'] == 0:
			json['result']['path'] = path
			json['result']['params'] = params
			return json['result'] if 'result' in json else None
		
		raise OmadaError(json)

	##
	## Perform a POST request and return the result.
	##
	def post(self, path, params={}, data=None, json=None):
		
		params['_'] = timestamp()
		params['token'] = self.token
		
		response = self.session.post( self.url_for(path), params=params, data=data, json=json )
		response.raise_for_status()
		# 		
		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None
		
		raise OmadaError(json)

	##
	## Perform a PATCH request and return the result.
	##
	def patch(self, path, params={}, data=None, json=None):
		
		params['_'] = timestamp()
		params['token'] = self.token
		
		response = self.session.patch( self.url_for(path), params=params, data=data, json=json )
		response.raise_for_status()
		
		json = response.json()
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None
		
		raise OmadaError(json)

	##
	## Get OmadacId to prefix request
	##
	def getApiInfo(self):

		response =  self.session.get( self.baseurl + '/api/info' )
		response.raise_for_status()
		
		json = response.json()
		
		if json['errorCode'] == 0:
			return json['result'] if 'result' in json else None
		
		raise OmadaError(json)

	##
	## Log in with the provided credentials and return the result.
	##
	def login(self, username=None, password=None):
		
		apiInfo = self.getApiInfo()
		if 'omadacId' in apiInfo:
			self.omadacId = apiInfo['omadacId']
			
		if username is None and password is None:
			if self.config is None:
				raise TypeError('username and password cannot be None')
			try:
				username = self.config['omada'].get('username')
				password = self.config['omada'].get('password')
			except:
				raise
		
		result = self.post( '/login', json={'username':username,'password':password} )
		self.token = result['token']
		self.currentUser = self.getCurrentUser()
		return result

	##
	## Log out of the current session. Return value is always None.
	##
	def logout(self):
		return self.post( '/logout' )

	##
	## Returns the current login status.
	##
	def getLoginStatus(self):
		return self.get( '/loginStatus' )

	##
	## Returns the current user information.
	##
	def getCurrentUser(self):
		return self.get( '/users/current' )

		## Group Types
	IPGroup   = 0 # "IP Group"
	PortGroup = 1 # "IP-Port Group"
	MACGroup  = 2 # "MAC Group"

	##
	## Returns the list of groups for the given site.
	##
	def getSiteGroups(self, site=None, type=None):
		
		site = self.site_key( site )
		
		if type is None:
			result = self.get( f'/sites/{site}/setting/profiles/groups' )
		else:
			result = self.get( f'/sites/{site}/setting/profiles/groups/{type}' )
		
		return result

	##
	## Returns the list of portal candidates for the given site.
	##
	## This is the "SSID & Network" list on Settings > Authentication > Portal > Basic Info.
	##
	def getPortalCandidates(self, site=None):
		
		site = self.site_key( site )
		
		return self.get( f'/sites/{site}/setting/portal/candidates' )

	##
	## Returns the list of RADIUS profiles for the given site.
	##
	def getRadiusProfiles(self, site=None):
		
		site = self.site_key( site )
		
		return self.get( f'/sites/{site}/setting/radiusProfiles' )

	##
	## Returns the list of scenarios.
	##
	def getScenarios(self):
		return self.get( '/scenarios' )

	##
	## Returns the list of all sites.
	##
	def getSites(self):
		return self.get_paged( f'/sites' )

	##
	## Returns the list of devices for given site.
	##
	def getSiteDevices(self, site=None):
		
		site = self.site_key( site )
		
		return self.get( f'/sites/{site}/devices' )

	##
	## Returns the list of active clients for given site.
	##
	def getSiteClients(self, site=None):
		
		site = self.site_key( site )
		
		return self.get_paged( f'/sites/{site}/clients', params={'filters.active':'true'} )

	##
	## Returns the list of alerts for given site.
	##
	def getSiteAlerts(self, site=None, archived=False, level=None, module=None, search=None):

		site = self.site_key( site )

		params = {}
		params['filters.archived'] = 'true' if archived else 'false'
		if level in ['Error', 'Warning', 'Information']:
			params['filters.level'] = level
		if module in ['Operation', 'System', 'Device', 'Client']:
			params['filters.module'] = module
		if search:
			params['searchKey'] = search
		return self.get_paged( f'/sites/{site}/alerts', params=params )

	##
	## Returns the list of events for given site.
	##
	def getSiteEvents(self, site=None, level=None, module=None, search=None):

		site = self.site_key( site )

		params = {}
		if level in ['Error', 'Warning', 'Information']:
			params['filters.level'] = level
		if module in ['Operation', 'System', 'Device', 'Client']:
			params['filters.module'] = module
		if search:
			params['searchKey'] = search
		return self.get_paged( f'/sites/{site}/events', params=params )

	##
	## Returns the notification settings for given site.
	##
	def getSiteNotifications(self, site=None):

		site = self.site_key( site )

		return self.get( f'/sites/{site}/notification' )

	##
	## Returns the list of settings for the given site.
	##
	def getSiteSettings(self, site=None):
		
		site = self.site_key( site )
		
		result = self.get( f'/sites/{site}/setting' )
		
		# work-around for error when sending PATCH for site settings (see below)
		if 'beaconControl' in result:
			if self.warnings:
				warnings.warn( "settings['beaconControl'] was removed as it causes an error", stacklevel=2 )
			del result['beaconControl']
		
		return result

	##
	## Push back the settings for the site.
	##
	def setSiteSettings(self, settings, site=None):
		
		site = self.site_key( site )
		
		# not sure why but setting 'beaconControl' here does not work, returns {'errorCode': -1001}
		if 'beaconControl' in settings:
			if self.warnings:
				warnings.warn( "settings['beaconControl'] was removed as it causes an error", stacklevel=2 )
			del settings['beaconControl']
		
		return self.patch( f'/sites/{site}/setting', json=settings )

	##
	## Returns the list of timerange profiles for the given site.
	##
	def getTimeRanges(self, site=None):
		
		site = self.site_key( site )
		
		return self.get( f'/sites/{site}/setting/profiles/timeranges' )

	##
	## Returns the list of wireless network groups.
	##
	## This is the "WLAN Group" list on Settings > Wireless Networks.
	##
	def getWirelessGroups(self, site=None):
		
		site = self.site_key( site )
		
		return self.get( f'/sites/{site}/setting/wlans' )

	##
	## Returns the list of wireless networks for the given group.
	##
	## This is the main SSID list on Settings > Wireless Networks.
	##
	def getWirelessNetworks(self, group, site=None):
		
		site = self.site_key( site )
		
		return self.get( f'/sites/{site}/setting/wlans/{group}/ssids' )
