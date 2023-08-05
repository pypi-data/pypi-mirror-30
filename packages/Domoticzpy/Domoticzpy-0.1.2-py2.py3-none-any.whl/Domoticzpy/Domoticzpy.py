#!/usr/bin/env python3=
# -*- coding: utf-8 -*-

import requests
import json
import sys


class Domoticzpy:
    """

    Simple class to use the Domoticz JSON API.
    Only tested with basic auth for the moment

    """

    def __init__(self, domoticz_url='', domoticz_user='', domoticz_password='' ):
        self.domoticz_url = domoticz_url
        self.domoticz_user = domoticz_user
        self.domoticz_password = domoticz_password
        return

    def __repr__(self):
        return "Domoticzpi: url({}), user({}), password({})".format(
                self.domoticz_url, self.domoticz_user, self.domoticz_password)

    def __Requests(self, command):
        r = requests.get(self.domoticz_url + command, auth=(self.domoticz_user,self.domoticz_password), verify=True)
        if r.status_code == 200:
            j=json.loads(r.text)
        else:
            print ('HTTP Error : ' + str(r.status_code))
            sys.exit(2)
        return(j)

    def getTemp(self):
        j=self.__Requests('type=devices&filter=temp&used=true&order=Name')
        return j['result']

    def getLight(self):
        j=self.__Requests('type=devices&filter=light&used=true&order=Name')
        return j['result']

    def getWeather(self):
        j=self.__Requests('type=devices&filter=weather&used=true&order=Name')
        for dev in j['result']:
            print (dev['Name'] + ' : ' + dev['Data'])

    def getUtility(self):
        j=self.__Requests('type=devices&filter=utility&used=true&order=Name')
        return j['result']

    def getSunrise(self):
        j=self.__Requests('type=command&param=getSunRiseSet')
        return j['Sunrise']

    def getSunset(self):
        j=self.__Requests('type=command&param=getSunRiseSet')
        return j['Sunset']

    def getLightSwitchesNames(self):
        j=self.__Requests('type=command&param=getlightswitches')
        return j['result']
