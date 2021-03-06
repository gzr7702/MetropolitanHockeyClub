##MetropolitanHockeyClub:
This is an application that can be used to track the teams and players of a local hockey team.
It can easily be modified to use for any small sports league. There is functionality to create,
read, update, and delete teams and players.

##Prerequisites:
- Python 2.7
- Flask 0.9
- Jinja2 2.7.2
- Werkzeug 0.8.3
- Sqlalchemy 0.8.4
- oauth2client 1.4.11
- httplib2 0.9.1
- requests 2.2.1

##Instalation:
To download the app, run:
git clone https://github.com/gzr7702/MetropolitanHockeyClub

No other installation is necessary if you have all the prerequisites

##Set Up:
To set up the database, run the following command:

python database_setup.py

To populate the database with existing data, load the respective csv files with players, teams
and users. Run this command:

python load_database.py

##How to run:
python project.py 

This will run the application with the dev server on port 5000

##Usage:
The application will only give you read access to all teams and players unless you log in using
your Google account. Once you are logged in, you can create, update and delete teams, add players to your teams,
update player info, and add free agents (players who are not asscociated with a team).
Players on your team can be accessed via your team's page.
