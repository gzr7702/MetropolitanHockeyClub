import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Team(Base):
	__tablename__ = 'team'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
	    return {
	    	'name': self.name,
	    	'owner': self.owner,
	    	'id': self.id,
	    	}


class Player(Base):
	__tablename__ = 'player'

	id = Column(Integer, primary_key = True)
	name =Column(String(80), nullable = False)
	position =Column(String(80), nullable = False)
	points = Column(Integer)
	team_id = Column(Integer,ForeignKey('team.id'))
	team = relationship(Team) 
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
	    return {
	    	'name': self.name,
	    	'position': self.position,
	    	'id': self.id,
	    	'points': self.points,
	    	'team_id': self.team_id,
	    	}


engine = create_engine('sqlite:///hockeyteams.db')

Base.metadata.create_all(engine)