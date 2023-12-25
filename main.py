from fastapi import FastAPI, WebSocket, Request, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from schema import *
from model import Base
from crud import *
from database import SessionLocal, engine
from typing import List

from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.responses import RedirectResponse

class NotAuthenticatedException(Exception):
    pass

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
SECRET="super-secret-key"

# html파일을 서비스할 수 있는 jinja설정 (/templates 폴더사용)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#Login_manager for login users
Login_manager=LoginManager(SECRET, '/login', use_cookie=True,
                     custom_exception = NotAuthenticatedException)
@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request:Request, exc: NotAuthenticatedException):
    return RedirectResponse(url='/login')

@Login_manager.user_loader()
def get_user(username:str, db:Session=None):
    if not db:
        with SessionLocal() as db:
            return db.query(User).filter(User.name == username).first()
    return db.query(User).filter(User.name == username).first()

@app.post('/token')
def login(response:Response, data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = get_user(username)
    if not user:
        raise InvalidCredentialsException
    if user.password != password:
        raise InvalidCredentialsException
    access_token = Login_manager.create_access_token(
        data = {'sub': username}
    )
    Login_manager.set_cookie(response, access_token)
    return {'access_token': access_token}

@app.post('/register')
def register_user(response: Response,
                  data: OAuth2PasswordRequestForm=Depends(),
                  db: Session = Depends(get_db)):
    username = data.username
    password = data.password

    user = db_register_user(db, username, password)
    if user:
        access_token = Login_manager.create_access_token(
            data= {'sub': username}
        )
        Login_manager.set_cookie(response, access_token)
        return "User created"
    else:
        return "Failed"

@app.get("/logout")
def logout(response:Response):
    response=RedirectResponse("/", status_code = 302)
    response.delete_cookie(key="access-token")
    return response

### WEBSOCKET AREA ###
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: object):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{data}")
    except Exception as e:
        pass
    finally:
        await manager.disconnect(websocket)

### WEBSOCKET AREA END###

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request":request})

@app.get("/friendlist")
async def friendlist_page(request: Request, db: Session = Depends(get_db), user=Depends(Login_manager)):
    friendlist_data = db_get_friends(db, user)
    return templates.TemplateResponse("friendlist.html", {"request": request, "friendlist_data": friendlist_data, "username": user.name})

@app.get("/chatlist")
async def chatlist_page(request: Request,  user=Depends(Login_manager)):
    return templates.TemplateResponse("chatlist.html", {"request": request, "username": user.name})

@app.get("/get_chatlist")
async def get_chatlist(db: Session = Depends(get_db), 
                       user=Depends(Login_manager)):
    return db_get_chatlist(db, user)


@app.get("/addfriend")
async def addfriend_page(request:Request):
    return templates.TemplateResponse("addfriend.html", {"request":request})

@app.get("/chatroom")
async def chatroom_page(request:Request, user=Depends(Login_manager)):
    return templates.TemplateResponse("chatroom.html", {"request":request, "username":user.name})

@app.post("/addfriend")
async def add_friend(response:Response, friend_id:FriendId,
                     db: Session = Depends(get_db), user= Depends(Login_manager)):
    sender = user.name
    receiver = friend_id.id
    result = db_add_friends(db, sender, receiver)
    response=RedirectResponse("/friendlist", status_code = 302)
    return response

@app.post("/into_chatroom")
async def into_chatroom(request: Request, friend_id: FriendId, db: Session = Depends(get_db), user=Depends(Login_manager)):
    userOne = user.name
    userTwo = friend_id.id
    chatroom_data = db_create_return_chatroom(db,userOne,userTwo)
    return chatroom_data

# message related functions below

@app.post("/get_chatlog", response_model = List[MessageSchema])
async def get_chatlog(chatid:ChatId, db:Session=Depends(get_db), user=Depends(Login_manager)):
    cid = chatid.id
    return db_get_chatlog(db, cid)

@app.post('/addmsg', response_model=MessageSchema)
async def add_msg(msgs: MessageSchemaBase, db: Session = Depends(get_db)):
    result = db_add_msgs(db, msgs)
    if not result:
        return None
    return result

@app.post('/update_latest')
async def update_latest(cr: ChatroomSchema, db: Session = Depends(get_db)):
    result = db_update_chatroom(db, cr)
    if not result:
        return None
    return result