"""
    flask_exp.py

    Experimentation with Flask and Strava v3 API    

"""


# all the imports
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, json
import requests
from tools.strava_api_v3_protocol import Strava_API_V3, Strava_API_Utilities, generate_strava_redirect_url, exchange_auth_code_for_token

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
    return render_template('index.html')


def have_strava_auth(): 
    try:
        a = session['strava_auth']
    except KeyError:
        return False
    else:
        return True


@app.route('/strava_compare', methods=['GET', 'POST'])
def strava_friends_summary():
    """ Strava athelete comparison """

    if not have_strava_auth():
        return redirect(url_for('get_strava_auth'))

    current_athlete = session['strava_auth']['athlete']

    strava_api = Strava_API_Utilities(session['strava_auth']['access_token'])
    friends_stats_summary = strava_api.get_friends_stats_summary()

    return render_template('athlete_summary.html', authenticated_athlete_info=current_athlete, friends_stats_summary=friends_stats_summary)


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
    return redirect(url_for('strava_friends_summary'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001, debug=True)

