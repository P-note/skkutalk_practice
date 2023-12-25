from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True)
    name = Column(String)
    password = Column(String)

class Friends(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key = True)
    userOne = Column(String)
    userTwo = Column(String)

class Chatrooms(Base):
    __tablename__ = "chatrooms"

    id = Column(Integer, primary_key = True)
    sender = Column(Integer)
    receiver = Column(Integer)
    latest = Column(String)

class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key = True)
    chatroom_id = Column(Integer)
    sender = Column(String)
    receiver = Column(String)
    content = Column(String)
    time = Column(String)
