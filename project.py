from flask import Flask, url_for, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Team, Base, Player

engine = create_engine('sqlite:///hockeyteams.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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
		#if name exists, throw an error
		if session.query(Player).filter_by(name = name).count() > 0:
			flash(name + " already exists!")
			# Is a flash enough to alert the user?
			print(name + " already exists!")
			return render_template('newplayer.html', team_id=team_id)
		new_player = Player(name, position, points, team_id)
		session.add(new_player)
		session.commit()
		flash("New Player created!")
		return redirect(url_for('showRoster', team_id=team_id))
	else:
		return render_template('newplayer.html', team_id=team_id)

@app.route('/team/<int:team_id>/roster/<int:player_id>/edit/')
def editPlayer(team_id, player_id):
	return render_template('editplayer.html', player=player, team=team)

@app.route('/team/<int:team_id>/roster/<int:player_id>/delete/')
def deletePlayer(team_id, player_id):
	if request.method == "POST":
		print "Postin', yo!"
	return render_template('deleteplayer.html', player=player, team=team)

@app.route('/teams/freeagents/')
def showFreeAgents():
	""" Show a list of Players and allow them to be added to a team. """
	players = session.query(Player).filter_by(team_id = 'null')
	return render_template('freeagents.html', players=players)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port=5000)