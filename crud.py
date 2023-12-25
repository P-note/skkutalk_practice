from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from schema import *
from model import *
from pydantic import BaseModel
from typing import Optional

def db_register_user(db: Session, name, password):
    db_item = User(name=name, password=password)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def db_add_friends(db: Session, sender, receiver):
    db_item = None
    if db.query(Friends).filter(and_(Friends.userOne == sender, Friends.userTwo == receiver)).first():
        return db_item  # None
    if db.query(Friends).filter(and_(Friends.userOne == receiver, Friends.userTwo == sender)).first():
        return db_item  # None

    if db.query(User).filter(User.name == receiver).first():
        db_item = Friends(userOne=sender, userTwo=receiver)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

    return db_item


def db_get_friends(db: Session, user: User):
    ans = (db.query(Friends).filter(or_(Friends.userOne == user.name, Friends.userTwo == user.name)).all())
    res = []
    for entry in ans:
        if entry.userOne == user.name:
            res.append(entry.userTwo)
        else:
            res.append(entry.userOne)

    return res

def db_get_chatlist(db: Session, user: User):
    return db.query(Chatrooms).filter(or_(Chatrooms.sender == user.name, Chatrooms.receiver == user.name)).all()

#create if chatroom doesn't exist; otherwise, just return chatroom.
def db_create_return_chatroom(db: Session, userOne, userTwo):
    r1 = (db.query(Chatrooms).filter(and_(Chatrooms.sender == userOne, Chatrooms.receiver == userTwo)).first())
    r2 = (db.query(Chatrooms).filter(and_(Chatrooms.sender == userTwo, Chatrooms.receiver == userOne)).first())
    if r1:
        return r1
    elif r2:
        return r2
    else:
        db_item = Chatrooms(sender=userOne, receiver=userTwo)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

def db_get_chatlog(db:Session, chatroom_id):
    return db.query(Messages).filter(Messages.chatroom_id == chatroom_id).all()

def db_add_msgs(db: Session, msgs: MessageSchema):
    db_item = Messages(
        chatroom_id=msgs.chatroom_id, sender=msgs.sender, receiver=msgs.receiver, content=msgs.content, time=msgs.time
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def db_update_chatroom(db:Session, cr:ChatroomSchema):
    res = db.query(Chatrooms).filter(Chatrooms.id == cr.id).one_or_none()
    if res:
        res.latest = cr.latest
        db.commit()
        db.refresh(res)
        return res
    return None