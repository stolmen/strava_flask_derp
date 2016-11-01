"""
    flask_exp.py

    Experimentation with Flask and Strava v3 API    

"""


# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json
import requests
from strava_api_v3_protocol import Strava_API_V3

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key',       # should be difficult to guess - keeps 'client side sessions' secure
    PORT='9001',
))

# Environment specific list of settings.
# Set environment variable FLASKR_SETTINGS to path of config file
app.config.from_envvar('FLASK_EXP_SETTINGS', silent=True)

# Strava specific things. TODO: move this to another module
STRAVA_AUTHORISE_URL = r'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = r'https://www.strava.com/oauth/token'
STRAVA_CLIENT_ID = 8613

# This is available in your private Strava developer landing
STRAVA_CLIENT_SECRET = 


@app.route('/')
def index():
    """ Index page """
    return render_template('index.html')


def have_strava_auth(): 
    try:
        a = session['strava_auth']
    except KeyError:
        return False
    else:
        return True

@app.route('/strava_compare', methods=['GET', 'POST'])
def strava_comparison():
    """ Strava athelete comparison. """

    # check for auth
    # if it doesn't exist, then redirect to auth page to get it, then come back. 
    if not have_strava_auth():
        return redirect(url_for('get_strava_auth'))

    protocol = Strava_API_V3(session['strava_auth']['access_token'])

    # get a list of friends and prompt to pick one.
    # TODO: chuck this into cookies or something to speed things up slightly.
    friends_list = protocol.list_athlete_friends()
    print(friends_list)

    # if POST command, then it's likely that an athlete was chosen to fight against
    # in which case, need to populate friend_target_comparison_info
    if request.method == 'POST':
        current_athlete = session['strava_auth']['athlete']

        # TODO - find a better fix. Seems that the request does not put True and False in quotes, so this has to be done before deserialisation... (JSON --> Dict) =__=
        target_athlete = json.loads(request.form['friend_id_to_compare'].replace('\'', '\"').replace("False", "\"False\"").replace("True", "\"True\""))
        friend_target_comparison_info = compare_two_strava_athletes(current_athlete, target_athlete)
    else:
        friend_target_comparison_info = None
        target_athlete = None

    return render_template('athlete_summary.html', athlete_info=current_athlete, friends=friends_list, friend_target_comparison_info=friend_target_comparison_info, chosen_friend=target_athlete)


def compare_two_strava_athletes(protocol, athlete_me, athlete_other):
    """ Compares two athlete summaries. """
    
    compare_dict = {
        'num_common_segments': 0,
        'num_common_segments_i_am_faster': 0, 
        'mean_speed_delta_over_all_common_segments': 0,
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


def get_condensed_effort_list(protocol, athlete):
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


# Below: OAuth2 authentication. 
@app.route('/strava_authenticate')
def get_strava_
    """ Gets strava auth token, chucks into app """
    
    # todo: handle an access denied authorisation code response from the Strava API
    if not have_strava_auth():
        return redirect(strava_redirect_url(client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET, redirect_uri=r'http://192.168.1.131:9001' + url_for('handle_auth_code')))


@app.route('/handle_auth_code')
def handle_auth_
    code = request.args.get('code')
    print(code)
    session['strava_auth'] = exchange_auth_code_for_token(client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET, auth_code=code)
    
    return redirect(url_for('strava_comparison'))


def exchange_auth_code_for_token(client_id, client_secret, auth_code):
    response = requests.post(STRAVA_TOKEN_URL, {'client_id': client_id, 'client_secret':client_secret, 'code': auth_code})
    return response.json()      # todo - handle exchange attempt failure case


def strava_redirect_url(client_id, client_secret, redirect_uri):    
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

