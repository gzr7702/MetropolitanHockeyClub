This is an application that can be used to track the teams and players of a local hockey team.
It can easily be modified to use for any small sports league.

Dependencies:

- Python 2.7
- Flask
- Sqlalchemy
- oauth2client
- httplib
- requests

Usage:

python project.py 

This will run the application with the dev server on port 5000

Todo:

- Make sure all functionality works:
	- free agents doesn't work
	- when you try to delete a team that's not yours, nothing happens
	- fix flash functionality

- Fix gdisconnect
- Take out Delete team from home screen and add a separate page? Add admin page and user?
- Double check all documentation
