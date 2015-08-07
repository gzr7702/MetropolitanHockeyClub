from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Team, Base, Player


engine = create_engine('sqlite:///hockeyteams.db')
Base.metadata.bind = engine
dbsession = sessionmaker(bind=engine)
session = dbsession()

