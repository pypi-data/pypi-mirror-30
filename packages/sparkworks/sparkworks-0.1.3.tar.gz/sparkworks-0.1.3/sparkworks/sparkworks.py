# -*- coding: utf-8 -*-
import requests
import os
import sys

sys.path.append(os.getcwd())

api_url = "https://api.sparkworks.net"
sso_url = "https://sso.sparkworks.net/aa/oauth/token"
token = {}

the_sites = []
the_site_resources = {}

class SparkWorks():
    __client_id = ""
    __client_secret = ""

    def __init__(self, client_id = None, client_secret = None):
        self.__client_id = client_id
        self.__client_secret = client_secret

    def connect(self, username, password):
        global token
        token = self.getToken(username, password)

    def getToken(self, username, password):
        params = {'username': username, 'password': password, 'grant_type': "password", 'client_id': self.__client_id,
              'client_secret': self.__client_secret}
        response = requests.post(sso_url, params)
        return response.json()

    def sites(self):
        global token, the_sites
        if len(the_sites) != 0:
            return the_sites
        else:
            response = self.apiGetAuthorized('/v1/location/site')
            the_sites = response.json()["sites"]
            return the_sites

    def main_site(self):
        for site in self.sites():
            if len(site["subsites"]) != 0:
                for user in site['sharedUsers']:
                    if properties.username == user['username'] and user['viewPermission'] and user['reusePermission']:
                        return site

    def rooms(self):
        _rooms = []
        for site in self.sites():
            if len(site["subsites"]) != 0:
                pass
            else:
                _rooms.append(site)
        return _rooms

    def select_rooms(self, room_names):
        _rooms = []
        for room_name in room_names:
            for site in self.sites():
                if site["name"].encode('utf-8') in room_name:
                    _rooms.append(site)
        return _rooms

    def siteResources(self, site):
        if site["id"] not in the_site_resources:
            response = self.apiGetAuthorized("/v1/location/site/" + str(site["id"]) + "/resource")
            the_site_resources[site["id"]] = response.json()["resources"]
        return the_site_resources[site["id"]]

    def siteResource(self, site, observedProperty):
        _resources = self.siteResources(site)
        for _resource in _resources:
            if _resource["uri"].startswith("site-") and _resource["property"] == observedProperty:
                return _resource

    def siteResourceDevice(self, site, observedProperty):
        _resources = self.siteResources(site)
        for _resource in _resources:
            if (_resource["uri"].startswith("00") is not 1)  and _resource["property"] == observedProperty:
                return _resource

    def siteResourceDeviceRPi(self, site, observedProperty):
        _resources = self.siteResources(site)
        for _resource in _resources:
            if _resource["uri"].startswith("gaia") and _resource["property"] == observedProperty:
                return _resource

    def siteResources_all(self, site, observedProperty):
        _selected_resources = []
        _resources = self.siteResources(site)
        for _resource in _resources:
            if observedProperty in _resource["property"]:
                _selected_resources.append(_resource)
        return _selected_resources

    def power_phases(self, site):
        _phases = {}
        _uris = []
        _resources = self.siteResources_all(site, "Power Consumption")
        for _resource in _resources:
            if not _resource["uri"].startswith("site-"):
                _phases[_resource["uri"]] = _resource
                _uris.append(_resource["uri"])
        _phases_ret = []
        for uri in sorted(_uris):
            _phases_ret.append(_phases[uri])
        return _phases_ret

    def current_phases(self, site):
        _phases = {}
        _uris = []
        _resources = self.siteResources_all(site, "Electrical Current")
        for _resource in _resources:
            if not _resource["uri"].startswith("site-"):
                _phases[_resource["uri"]] = _resource
                _uris.append(_resource["uri"])
        _phases_ret = []
        for uri in sorted(_uris):
            _phases_ret.append(_phases[uri])
        return _phases_ret

    def total_power(self, site):
        _resources = self.siteResources_all(site, "Power Consumption")
        for _resource in _resources:
            if _resource["uri"].startswith("site-"):
                return _resource

    def latest(self,resource):
        response = self.apiGetAuthorized('/v1/resource/' + str(resource["resourceId"]) + '/latest')
        return response.json()

    def summary(self, resource):
        response = self.apiGetAuthorized('/v1/resource/' + str(resource["resourceId"]) + '/summary')
        return response.json()

    def resource(self, uri):
        response = self.apiGetAuthorized('/v1/resource/uri/' + uri)
        return response.json()

    def resources(self):
        response = self.apiGetAuthorized('/v1/resource')
        return response.json()["resources"]

    def apiGetAuthorized(self, path):
        return requests.get(api_url + path, headers={'Authorization': 'Bearer ' + token["access_token"]})
