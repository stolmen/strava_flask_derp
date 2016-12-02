"""
    (A start of) Wrapper of RESTful Strava V3 API as described in http://strava.github.io/api/v3
    Edward Ong Oct-2016

    TODO: move authentication steps here. Wrap more things. Perhaps use stravalib instead. 
"""


import requests

# Strava specific things. TODO: move this to another module
STRAVA_AUTHORISE_URL = r'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = r'https://www.strava.com/oauth/token'
API_BASE_URL = 'https://www.strava.com/api/v3/'

class Strava_API_V3(object):
    
    def __init__(self, access_token):
        self.access_token = access_token

    def _return_get_response(self, url_extension, **kwargs):
        url = API_BASE_URL + url_extension
        data = self._return_data_dict_with_access_token_inserted(kwargs)
        return requests.get(url, data=kwargs).json()

    def _return_data_dict_with_access_token_inserted(self, data_dict):
        if data_dict == None:
            data_dict = {'access_token': self.access_token}
        else:
            data_dict['access_token'] = self.access_token
        return data_dict

    def list_athlete_friends(self, id=None):
        return self._return_get_response(self._list_athlete_friends_url(id))

    def _list_athlete_friends_url(self, id=None):
        if id is not None:
            return 'athlete/{}/friends'.format(id)
        else:
            return 'athlete/friends'

    def list_recent_followers_activities(self):
        return self._return_get_response('activities/following', page=1, per_page=200)
        

#class Strava_Extensions(Strava_API_V3):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)


# TODO: refactor these nicely
# Authentication

def generate_strava_redirect_url(client_id, client_secret, redirect_uri):    
    # TODO: utilise requests module for URL construction
    parameters = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
#        'scope': ' ',
        'state': 'dummy_state',
        'approval_prompt': 'auto',
        'response_type': 'code',
    }

    print(parameters['redirect_uri'])
    parameters_string = '&'.join(['{}={}'.format(key, value) for key, value in parameters.items()])

    return "{}?{}".format(STRAVA_AUTHORISE_URL, parameters_string)


def exchange_auth_code_for_token(client_id, client_secret, auth_code):
    response = requests.post(STRAVA_TOKEN_URL, {'client_id': client_id, 'client_secret':client_secret, 'code': auth_code})
    return response.json()      # todo - handle exchange attempt failure case

