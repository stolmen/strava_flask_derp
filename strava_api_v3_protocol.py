"""
    (A start of) Wrapper of RESTful Strava V3 API as described in http://strava.github.io/api/v3
    Edward Ong Oct-2016

    TODO: move authentication steps here. Wrap more things. Perhaps use stravalib instead. 
"""


import requests

class Strava_API_V3(object):
    API_BASE_URL = 'https://www.strava.com/api/v3/'
    def __init__(self, access_token):
        self.access_token = access_token

    def _return_get_response(self, url_extension, **kwargs):
        url = self.API_BASE_URL + url_extension

        if kwargs == None:
            kwargs = {'access_token': self.access_token}
        else:
            kwargs['access_token'] = self.access_token
        
        return requests.get(url, data=kwargs).json()

    def list_athlete_friends(self, id=None):
        if id:
            url = 'athlete/{}/friends'.format(id)
        else:
            url = 'athlete/friends'
        
        return self._return_get_response(url)

    def list_recent_followers_activities(self):
        return self._return_get_response('activities/following', page=1, per_page=200)
        


class Strava_Extensions(Strava_API_V3):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

