from flask import Flask, url_for, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

@app.route('/')
@app.route('/teams/')
def showTeams():
	return 'This page shows the teams'

@app.route('/teams/new')
def newTeam():
	return 'This page will allow a team to be added'

@app.route('/teams/<int:team_id>/edit/')
def editTeam():
	return 'This page will allow someone to edit a team'

@app.route('/teams/<int:team_id>/delete/')
def deleteTeam(team_id):
	return 'This page will allow someone to delete a team'

@app.route('/teams/<int:team_id>/')
@app.route('/teams/<int:team_id>/roster')
def showRoster(team_id):
	return 'This page will the roster for a team'

@app.route('/team/<int:team_id>/roster/new/')
def addPlayer(team_id):
	return 'This page will allow someone to add a new player'

@app.route('/team/<int:team_id>/roster/edit/')
def editPlayer(team_id):
	return 'This page will allow someone to edit the info for a player'

@app.route('/team/<int:team_id>/roster/delete/')
def deletePlayer(team_id):
	return 'This page will allow someone to delete the info for a player'

if __name__ == '__main__':
	#app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port=5000)