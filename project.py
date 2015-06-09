from flask import Flask, url_for, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Team, Base, Player

engine = create_engine('sqlite:///hockeyteams.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Need to add functionality to api for players/teams that are not found!
# Here is our JSON api:
@app.route('/teams/JSON/')
def teamsJSON():
	teams = session.query(Team).all()
	return jsonify(Teams=[t.serialize for t in teams])

@app.route('/teams/<int:team_id>/roster/JSON/')
def teamRosterJSON(team_id):
	team = session.query(Team).filter_by(id = team_id).one()
	players = session.query(Player).filter_by(team_id = team.id)
	return jsonify(Players=[p.serialize for p in players])

@app.route('/player/<int:player_id>/JSON/')
def playerJSON(player_id):
	player = session.query(Player).filter_by(id = player_id).one()
	return jsonify(player.serialize)

# Here are our pages:
@app.route('/')
@app.route('/home/')
def showTeams():
	""" The home page. Shows all teams"""
	teams = session.query(Team).all()
	return render_template('home.html', teams=teams)

@app.route('/teams/new/', methods=['GET', 'POST'])
def newTeam():
	""" Add a new team """
	if request.method == 'POST':
		name = request.form['name']
		owner = request.form['owner']
		new_team = Team(name, owner)
		session.add(new_team)
		session.commit()
		flash("New team created!")
		return redirect(url_for('showTeams'))
	else:
		return render_template('newteam.html')

@app.route('/teams/<int:team_id>/delete/', methods=['GET', 'POST'])
def deleteTeam(team_id):
	""" Delete Team and disassociate all its players from the team."""
	team = session.query(Team).filter_by(id = team_id).one()
	players = session.query(Player).filter_by(team_id = team.id)
	if request.method == 'POST':
		for player in players:
			player.team = None
		session.delete(team)
		session.commit()
		flash("Team deleted!")
		return redirect(url_for('showTeams'))
	else:
		return render_template('deleteteam.html', team=team, team_id=team_id)

@app.route('/teams/<int:team_id>/')
@app.route('/teams/<int:team_id>/roster/')
def showRoster(team_id):
	team = session.query(Team).filter_by(id = team_id).one()
	players = session.query(Player).filter_by(team_id = team.id)
	return render_template('team.html', team=team, players=players)

@app.route('/team/<int:team_id>/roster/new/', methods=['GET', 'POST'])
def addPlayer(team_id): 
	if request.method == 'POST':
		name = request.form['name']
		position = request.form['position']
		points = request.form['points']
		#if name already exists, return to form
		if session.query(Player).filter_by(name = name).count() > 0:
			# Is a flash enough to alert the user? ==================
			flash(name + " already exists!")
			return render_template('newplayer.html', team_id=team_id)
		new_player = Player(name, position, points, team_id)
		session.add(new_player)
		session.commit()
		flash("New Player created!")
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('newplayer.html', team_id=team_id)

@app.route('/team/<int:team_id>/roster/<int:player_id>/edit/', methods=['GET', 'POST'])
def editPlayer(team_id, player_id):
	""" Edit the position or points of a particular player """
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
	player = session.query(Player).filter_by(id = player_id).one()
	if request.method == 'POST':
		session.delete(player)
		session.commit()
		flash("Player " + player.name + " deleted!")
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('deleteplayer.html', player=player, team_id=team_id)

@app.route('/teams/freeagents/')
def showFreeAgents():
	""" Show a list of Players and allow them to be added to a team. """
	# This is broken until we add user IDs. Need to add player to the user's team ===============
	# for now, we set team id to 1 just to redirect somewhere
	team_id = 3
	players = session.query(Player).filter_by(team_id = 'null')
	return render_template('freeagents.html', players=players, team_id=team_id)

@app.route('/team/<int:team_id>/addplayer/<int:player_id>/', methods=['GET', 'POST'])
def addPlayerToTeam(team_id, player_id):
	""" Add player to current user's team """
	player = session.query(Player).filter_by(id = player_id).one()
	if request.method == 'POST':
		player.team_id = team_id
		session.commit()
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('addplayer.html', player=player, team_id=team_id)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port=5000)