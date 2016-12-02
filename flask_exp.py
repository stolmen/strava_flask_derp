"""
    flask_exp.py

    Experimentation with Flask and Strava v3 API    

"""


# all the imports
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, json
import requests
from tools.strava_api_v3_protocol import Strava_API_V3, generate_strava_redirect_url, exchange_auth_code_for_token

# These should really be stored as environment variables and not in any code!
# from client_secret import STRAVA_CLIENT_SECRET, STRAVA_CLIENT_ID 

STRAVA_CLIENT_ID = os.environ['STRAVA_CLIENT_ID']
STRAVA_CLIENT_SECRET = os.environ['STRAVA_CLIENT_SECRET']

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key',    # should be difficult to guess - keeps 'client side sessions' secure
))

# Environment specific list of settings.
# Set environment variable FLASKR_SETTINGS to path of config file
app.config.from_envvar('FLASK_EXP_SETTINGS', silent=True)


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
    """ Strava athelete comparison """

    if not have_strava_auth():
        return redirect(url_for('get_strava_auth'))

    protocol = Strava_API_V3(session['strava_auth']['access_token'])

    # get a list of friends and prompt to pick one.
    # TODO: chuck this into cookies or something to speed things up slightly.
    friends_list = protocol.list_athlete_friends()
    print(friends_list)

    current_athlete = session['strava_auth']['athlete']

    # if POST command, then it's likely that an athlete was chosen to fight against
    # in which case, need to populate friend_target_comparison_info
    if request.method == 'POST':
        # TODO - find a better fix. Seems that the request does not put True and False in quotes, so this has to be done before deserialisation... (JSON --> Dict) =__=
        target_athlete_info_string = request.form['friend_id_to_compare']
        print("Info string: {}".format(target_athlete_info_string))
        target_athlete = json.loads(target_athlete_info_string.replace('\'', '\"').replace("False", "\"False\"").replace("True", "\"True\"").replace("None", "\"None\"").replace("u\"", "\""))
        current_athlete_recent_activities, target_athlete_recent_activities = recent_activites_filtered(protocol, current_athlete), recent_activites_filtered(protocol, target_athlete)

        kudos_totals = [num_kudos_per_follower_in_activites(activity_list) for activity_list in (current_athlete_recent_activities, target_athlete_recent_activities)] 
        achievement_comparison = [num_achievements_in_activites(activity_list) for activity_list in (current_athlete_recent_activities, target_athlete_recent_activities)]

        friend_target_comparison_info = {
            'kudos_comparison': kudos_totals,
            'achievement_comparison': achievement_comparison,
        }

    else:
        friend_target_comparison_info = None
        target_athlete = None

    return render_template('athlete_summary.html', athlete_info=current_athlete, friends=friends_list, friend_target_comparison_info=friend_target_comparison_info, chosen_friend=target_athlete)


def recent_activites_filtered(protocol, athlete):
    list_of_activities = protocol.list_recent_followers_activities()
    return [i for i in list_of_activities if i['athlete']['id'] == athlete['id']]
    


def num_kudos_per_follower_in_activites(activity_list):
    kudos_sum = 0    
    for activity in activity_list:
        kudos_sum += activity['kudos_count']
    return kudos_sum


def num_achievements_in_activites(activity_list):
    achievements_sum = 0
    for activity in activity_list:
        achievements_sum += activity['achievement_count']
    return achievements_sum


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


# Below: OAuth2 authentication. 
@app.route('/strava_authenticate')
def get_strava_auth():
    """ Gets strava auth token, chucks into app """
    # todo: handle an access denied authorisation code response from the Strava API
    if not have_strava_auth():
        # todo: remove hardcoded domain name
        return redirect(generate_strava_redirect_url(client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET, redirect_uri=os.environ['STRAVA_API_REDIRECT_URI'] + url_for('handle_auth_code')))


@app.route('/handle_auth_code')
def handle_auth_code():
    code = request.args.get('code')
    session['strava_auth'] = exchange_auth_code_for_token(client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET, auth_code=code)
    return redirect(url_for('strava_comparison'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001, debug=True)

