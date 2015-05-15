import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()


class Team(Base):
	__tablename__ = 'team'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	owner = Column(String(250), nullable=False)

class Player(Base):
	__tablename__ = 'player'

	name =Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	position =Column(String(80), nullable = False)
	points = Column(Integer)
	team_id = Column(Integer,ForeignKey('team.id'))
	team = relationship(Team) 

	@property
	def serialize(self):
	    return {
	    	'name': self.name,
	    	'position': self.position,
	    	'id': self.id,
	    	'points': self.points,
	    	'penalty_minutes': self.penalty_minutes,
	    	}


engine = create_engine('sqlite:///hockeyteams.db')

Base.metadata.create_all(engine)