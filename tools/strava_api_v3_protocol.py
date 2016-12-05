"""
    (A start of) Wrapper of RESTful Strava V3 API as described in http://strava.github.io/api/v3
    Edward Ong Oct-2016

    TODO: move authentication steps here. Wrap more things. Perhaps use stravalib instead. 
"""


import requests
from collections import namedtuple

# Strava specific things. TODO: move this to another module
STRAVA_AUTHORISE_URL = r'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = r'https://www.strava.com/oauth/token'
API_BASE_URL = 'https://www.strava.com/api/v3/'


FriendSummary = namedtuple('FriendSummary', ['full_name', 'total_num_recent_kudos', 'total_num_recent_achievements'])


class Strava_API_V3(object):
    """ Low level accesse to API. """
    
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

    def list_athlete_friends_including_athlete(self, id=None):
        return self.list_athlete_friends() + [self.authenticated_athlete]

    @property
    def authenticated_athlete(self):
        return self._return_get_response('athlete')

    def list_athlete_friends(self, id=None):
        """ Not inclusive of the target athlete. """
        return self._return_get_response(self._list_athlete_friends_url(id))

    def _list_athlete_friends_url(self, id=None):
        if id is not None:
            return 'athlete/{}/friends'.format(id)
        else:
            return 'athlete/friends'

    def list_recent_followers_activities(self):
        return self._return_get_response('activities/following', page=1, per_page=200)


class Strava_API_Utilities(Strava_API_V3):
    """ Defines some higher level functionality. """    
    def __init__(self, *args, **kwargs):
        Strava_API_V3.__init__(self, *args, **kwargs)

    def get_friends_stats_summary(self):
        """ For the authenticated user, generates a list of dicts. 
        Each element of the list contains stats of a particular friend.
       
        Stats are generated from the last 200 or so activities from your personal feed.
        This is a limitation of the Strava API. Of course it would be great if the 
        API allowed full access to all followers' activities, but sadly, this is not the case."""
        
        summary = []
        self.recent_activities = self.list_recent_followers_activities()
        for friend in self.list_athlete_friends_including_athlete():
            summary.append(FriendSummary(
                full_name="{} {}".format(friend['firstname'], friend['lastname']), 
                total_num_recent_kudos=self.sum_kudos_in_recent_activities(friend['id']),
                total_num_recent_achievements=self.sum_achievements_in_recent_activities(friend['id']))
            )
        return summary

    def sum_kudos_in_recent_activities(self, athlete_id):
        kudos_sum = 0
        for activitiy in self.recent_activities_filtered_by_id(athlete_id):
            kudos_sum += activitiy['kudos_count']
        return kudos_sum

    def sum_achievements_in_recent_activities(self, athlete_id):
        achievement_sum = 0
        for activitiy in self.recent_activities_filtered_by_id(athlete_id):
            achievement_sum += activitiy['achievement_count']
        return achievement_sum

    def recent_activities_filtered_by_id(self, athlete_id):
        return [i for i in self.recent_activities if i['athlete']['id'] == athlete_id]


def compare_two_strava_athletes(protocol, athlete_me, athlete_other):
    """ Compares two athlete summaries. """
    
    compare_dict = {
        
    }

    common_segments = get_list_of_effort_pairs_that_share_segment(protocol, athlete_me, athlete_other)
    compare_dict['num_common_segments'] = len(common_segments)
    
    speed_deltas = []
    for my_effort, other_effort in common_segments:
        # compute average moving speed
        my_effort_moving_average = calculate_moving_average_speed(my_effort)
        other_effort_moving_average = calculate_moving_average_speed(other_effort)
        
        if my_effort_moving_average > other_effort_moving_average:
            compare_dict['num_common_seguments_i_am_faster'] += 1

        speed_deltas.append(my_effort_moving_average - other_effort_moving_average)

    compare_dict['mean_speed_delta_over_all_common_segments'] = float(sum(speed_deltas)) / len(speed_deltas)
    return compare_dict


def get_list_of_effort_pairs_that_share_segment(protocol, athlete_me, athlete_other):
    athlete_me_id = athlete_me['id']
    athlete_other_id = athlete_other['id']

    # get condensed list of efforts for both athletes
    # NOTE when implementing: need to get DETAILED view which requies lots of API accesses... Probably best to grab a dataset from a random person to test first hha.
    efforts_list_condensed_me = get_condensed_effort_list(protocol, athlete_me)
    efforts_list_condensed_other = get_condensed_effort_list(protocol, athlete_other)

    # TODO: check that there are no entries that contain the same segment ID (i.e. checking that effort_list_condensed_xxx are in fact condensed!)

    # now group into pairs that share the same segment id
    effort_pairs = []
    for my_effort in efforts_list_condense_me:
        for other_effort in efforts_list_condensed_other:
            if my_effort['segment']['id'] == other_effort['segment']['id']:
                effort_pairs.append(my_effort, other_effort)
                break
    
    return effort_pairs


# def get_condensed_effort_list(protocol, athlete):
    # INCOMPLETE
    # Implementation plan:
    # from athlete, get list of summary activities
        # NOTE: API doesn't seem to support this functionality, presumably for privacy purposes...
        # alternatives; 
        # 1) Scan through entire list of activites, efforts or segments and then match by ID (impractical)
        # 2) Use GET https://www.strava.com/api/v3/activities/following - but this only uses the last 200 total activites from all your followers. 
        #           this will be more accurate the less follows that someone has... So it may be possible to temporarily unfollow lots of people, and re-follow.. If at all possible..
        # 3) Only use KOMs or top 10s
        # 4) 

    # from each summary activity, get detailed activity

    # from each detailed activity, get all efforts

    # from effort list, extract only the best times
        

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

