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

@app.route('/teams/new/')
def newTeam():
	""" Add a new team """
	if request.method == 'POST':
		new_team = Team(name = request.form['name'], team_id = team_id)
		owner = Team(name = request.form['owner'], team_id = team_id)
		session.add(new_team)
		session.add(owner)
		session.commit()
		flash("New team created!")
		return redirect(url_for('showTeams'))
	else:
		return render_template('newteam.html')

@app.route('/teams/<int:team_id>/edit/')
def editTeam(team_id):
	""" This page will allow someone to edit a full team at one time."""
	return render_template('editteam.html', team=team, players=players)

@app.route('/teams/<int:team_id>/delete/')
def deleteTeam(team_id):
	if request.method == 'POST':
		print "Posting"
	return render_template('deleteteam.html', team=team, team_id=1)

@app.route('/teams/<int:team_id>/')
@app.route('/teams/<int:team_id>/roster/')
def showRoster(team_id):
	team = session.query(Team).filter_by(id = team_id).one()
	players = session.query(Player).filter_by(team_id = team.id)
	return render_template('team.html', team=team, players=players)

@app.route('/team/<int:team_id>/roster/new/')
def addPlayer(team_id):
	return render_template('newplayer.html')

@app.route('/team/<int:team_id>/roster/<int:player_id>/edit/')
def editPlayer(team_id, player_id):
	return render_template('editplayer.html', player=player, team=team)

@app.route('/team/<int:team_id>/roster/<int:player_id>/delete/')
def deletePlayer(team_id, player_id):
	if request.method == "POST":
		print "Postin', yo!"
	return render_template('deleteplayer.html', player=player, team=team)

if __name__ == '__main__':
	#app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port=5000)