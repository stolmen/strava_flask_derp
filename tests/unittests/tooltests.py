import unittest
import os

from tools.strava_api_v3_protocol import Strava_API_V3, generate_strava_redirect_url, exchange_auth_code_for_token

class StravaApiClassTests(unittest.TestCase):
    """ API not tested. Just that the correct """

    def setUp(self):
        self.api = Strava_API_V3(1)

    def test_class_creation(self):
        """ Strava API object creation """
        a = Strava_API_V3(1)

    def test_insertion_of_token_into_data_dict(self):
        """ Token insertion into data argument of request """       
        self.assertEquals(self.api._return_data_dict_with_access_token_inserted(None), {'access_token': self.api.access_token})
        self.assertEquals(self.api._return_data_dict_with_access_token_inserted({}), {'access_token': self.api.access_token})
        self.assertEquals(self.api._return_data_dict_with_access_token_inserted({'a': 1}), {'a': 1, 'access_token': self.api.access_token})

    def test_request_response(self):
        # nothing here now
        # Perhaps here we could test the addition of the access token - when there is and 
        # when there isn't an access token availble. 
        print 'dummy test'

    def test_get_friends_list_url(self):
        """ Friends list URL generation """
        self.assertEquals(self.api._list_athlete_friends_url(), 'athlete/friends')
        self.assertEquals(self.api._list_athlete_friends_url(1), 'athlete/1/friends')

class StravaApiUtilMethodsTests(unittest.TestCase):
    def test_generate_strava_redirect_url(self):
        print 'dummy test'

    

if __name__ == '__main__':
    unittest.main()

#class StravaRedirectUrlGenerationTests(unittest.Testcase):
   
