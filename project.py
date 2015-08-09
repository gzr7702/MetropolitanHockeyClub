from flask import Flask, url_for, render_template, request, redirect, url_for, flash, jsonify, abort

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Team, Base, Player, User

# imports for oauth2
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_ID = "MetropolitanHockeyClub"

# Create database session for sqlalchemy
engine = create_engine('sqlite:///hockeyteams.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# --------------------------------------------------------------------
# Here is our JSON api 
# Includes: team, free agents, team rosters, individual players
# --------------------------------------------------------------------
# Need to add functionality to api for players/teams that are not found? ==============================

@app.route('/teams/JSON/')
def teamsJSON():
	""" Return JSON of all teams in the league"""
	teams = session.query(Team).all()
	return jsonify(Teams=[t.serialize for t in teams])

@app.route('/teams/freeagents/JSON/')
def freeAgentsJSON():
	""" Return JSON of Players that are not associated with a team. """
	players = session.query(Player).filter_by(team_id = None)
	return jsonify(Players=[p.serialize for p in players])

@app.route('/teams/<int:team_id>/JSON/')
@app.route('/teams/<int:team_id>/roster/JSON/')
def teamRosterJSON(team_id):
	try:
		session.query(Player).filter_by(team_id = team_id).count()
	except:
		return jsonify("Error")
	team = session.query(Team).filter_by(id = team_id).one()
	players = session.query(Player).filter_by(team_id = team.id)
	return jsonify(Players=[p.serialize for p in players])

@app.route('/player/<int:player_id>/JSON/')
def playerJSON(player_id):
	player = session.query(Player).filter_by(id = player_id).one()
	return jsonify(player.serialize)

# --------------------------------------------------------------------
# Functionality for login
# --------------------------------------------------------------------

# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# --------------------------------------------------------------------
# Here are our pages 
# --------------------------------------------------------------------
@app.route('/')
@app.route('/home/')
def showTeams():
	""" The home page. Shows all teams"""
	teams = session.query(Team).all()
	if 'username' not in login_session:
		return render_template('publichome.html', teams=teams)
	else:
		return render_template('home.html', teams=teams, username=login_session['username'])

@app.route('/teams/new/', methods=['GET', 'POST'])
def newTeam():
	""" Add a new team """
	if 'username' not in login_session:
		return redirect('/login/')
	if request.method == 'POST':
		name = request.form['name']
		user_id = getUserID(login_session['email'])
		new_team = Team(name=name, user_id=user_id)
		session.add(new_team)
		session.commit()
		flash("New team " + new_team.name + " created!")
		return redirect(url_for('showTeams'))
	else:
		return render_template('newteam.html', username=login_session['username'])

@app.route('/teams/<int:team_id>/delete/', methods=['GET', 'POST'])
def deleteTeam(team_id):
	""" Delete Team and disassociate all its players from the team."""
	if 'username' not in login_session:
		return redirect('/login/')
	team = session.query(Team).filter_by(id = team_id).one()
	players = session.query(Player).filter_by(team_id = team.id)
	creator = team.user_id
	user_id = getUserID(login_session['email'])
	#import pdb; pdb.set_trace()
	if request.method == 'POST' and creator == user_id:
		for player in players:
			player.team = None
		session.delete(team)
		session.commit()
		flash(team.name + " deleted!")
		return redirect(url_for('showTeams'))
	else:
		return render_template('deleteteam.html', team=team, team_id=team_id)

@app.route('/teams/<int:team_id>/')
@app.route('/teams/<int:team_id>/roster/')
def showRoster(team_id):
	team = session.query(Team).filter_by(id = team_id).one()
	creator = team.user_id
	if session.query(Player).filter_by(team_id = team.id).count() > 0:
		players = session.query(Player).filter_by(team_id = team.id).all()
	else:
		players = None

	if 'username' not in login_session or creator != getUserID(login_session['email']):
		return render_template('publicteam.html', team=team, players=players, creator=creator)
	else:
		return render_template('team.html', team=team, players=players, creator=creator)

@app.route('/team/<int:team_id>/roster/new/', methods=['GET', 'POST'])
def addPlayer(team_id): 
	if 'username' not in login_session:
		return redirect('/login/')
	if request.method == 'POST':
		name = request.form['name']
		position = request.form['position']
		points = request.form['points']
		team = session.query(Team).filter_by(id = team_id).one()
		user = getUserInfo(team.user_id)
		creator = getUserID(user.email)
		#if name already exists, return to form
		if session.query(Player).filter_by(name = name).count() > 0:
			message = "Player " + name + " already exists! Please add a different player."
			flash(message)
			return render_template('newplayer.html', team_id=team_id)
		new_player = Player(name=name, position=position, points=points, team_id=team_id, user_id=creator)
		session.add(new_player)
		session.commit()
		flash("New Player created!")
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('newplayer.html', team_id=team_id)

@app.route('/addfreeagent/', methods=['GET', 'POST'])
def addFreeAgent(): 
	if 'username' not in login_session:
		return redirect('/login/')
	if request.method == 'POST':
		name = request.form['name']
		position = request.form['position']
		points = request.form['points']
		user_email = login_session['email']
		creator = getUserID(user_email)
		#if name already exists, return to form
		if session.query(Player).filter_by(name = name).count() > 0:
			message = "Player " + name + " already exists! Please add a different player."
			flash(message)
			return render_template('newfreeagent.html')
		new_player = Player(name=name, position=position, points=points, team_id=None, user_id=creator)
		session.add(new_player)
		session.commit()
		flash("New free agent " + name + " created!")
		return redirect('/')
	else:
		return render_template('newfreeagent.html')


@app.route('/team/<int:team_id>/roster/<int:player_id>/edit/', methods=['GET', 'POST'])
def editPlayer(team_id, player_id):
	""" Edit the position or points of a particular player """
	if 'username' not in login_session:
		return redirect('/login/')
	player = session.query(Player).filter_by(id = player_id).one()
	if request.method == 'POST':
		position = request.form['position']
		points = request.form['points']
		if position != player.position:
			player.position = position
		if points != player.points:
			player.points = points
		session.commit()
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('editplayer.html', player=player)

@app.route('/team/<int:team_id>/roster/<int:player_id>/delete/', methods=['GET', 'POST'])
def deletePlayer(team_id, player_id):
	""" Delete Team and disassociate all its players from the team."""
	if 'username' not in login_session:
		return redirect('/login/')
	player = session.query(Player).filter_by(id = player_id).one()
	if request.method == 'POST':
		session.delete(player)
		session.commit()
		flash("Player " + player.name + " deleted!")
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('deleteplayer.html', player=player, team_id=team_id)

@app.route('/teams/freeagents/')
@app.route('/teams/<int:team_id>/freeagents/')
def showFreeAgents(team_id=None):
	""" Show a list of Players and allow them to be added to a team. """
	team_id = team_id
	players = session.query(Player).filter_by(team_id = None).all()
	if 'username' not in login_session:
		return render_template('publicfreeagents.html', players=players)
	else:
		return render_template('freeagents.html', players=players, team_id=team_id)

@app.route('/team/<int:team_id>/addplayer/<int:player_id>/', methods=['GET', 'POST'])
def addPlayerToTeam(team_id, player_id):
	""" Add player to current user's team """
	if 'username' not in login_session:
		return redirect('/login/')
	player = session.query(Player).filter_by(id = player_id).one()
	if request.method == 'POST':
		player.team_id = team_id
		session.commit()
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('addplayer.html', player=player, team_id=team_id)

@app.route('/about/')
def about():
	""" The information page""" 
	return render_template('about.html')

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port=5000)