from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    id: Optional[int]
    name: str
    password: str

    class Config:
        orm_mode = True

class FriendSchemaBase(BaseModel):
    userOne: Optional[str]
    userTwo: Optional[str]

class FriendSchema(FriendSchemaBase):
    id: Optional[int]
    class Config:
        orm_mode=True

class ChatroomSchemaBase(BaseModel):
    sender:Optional[str]
    receiver:Optional[str]

class ChatroomSchema(ChatroomSchemaBase):
    id: Optional[int]
    latest: Optional[str]
    class Config:
        orm_mode=True

class MessageSchemaBase(BaseModel):
    chatroom_id: Optional[int]
    sender:Optional[str]
    receiver:Optional[str]
    content: Optional[str]
    time: Optional[str]

class MessageSchema(MessageSchemaBase):
    id:Optional[int]
    class Config:
        orm_mode=True

class FriendId(BaseModel):
    id: Optional[str]

class ChatId(BaseModel):
    id: Optional[str]