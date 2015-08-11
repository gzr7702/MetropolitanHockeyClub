""" A Basic Script to load sample data"""

import sqlite3
import csv

def main():
	# Connect to the database
	conn = sqlite3.connect('../hockeyteams.db')
	cursor = conn.cursor()

	# Read in user data and write to the database
	with open('users.csv') as uf:
		reader = csv.reader(uf)
		for row in reader:
			command = "INSERT INTO user (name, email, picture) VALUES (?, ?, ?);"
			tuple(row)
			cursor.execute(command, row)

	# Read in team data and write to the database
	with open('teams.csv') as tf:
		reader = csv.reader(tf)
		for row in reader:
			command = "INSERT INTO team (name, user_id) VALUES (?, ?);"
			tuple(row)
			cursor.execute(command, row)

	# Read in player data and write to the database
	with open('players.csv') as pf:
		reader = csv.reader(pf)
		for row in reader:
			command = "INSERT INTO player (name, position, points, team_id, user_id) VALUES (?, ?, ?, ?, ?);"
			tuple(row)
			cursor.execute(command, row)

	# write to the database
	conn.commit()
	conn.close()

if __name__ == '__main__':
	main()