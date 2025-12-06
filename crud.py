from fastapi import FastAPI, HTTPException, status, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Messages CRUD")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
                   )

# Настройка Jinja2 и статических файлов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Модель для входных данных (запросов: создание и обновление)
class MessageCreate(BaseModel):
    content: str

class MessageUpdate(BaseModel):
    content: str | None = None

# Модель для ответов и хранения в базе данных
class Message(BaseModel):
    id: int
    content: str


# Инициализируем messages_db как список объектов Message
messages_db: List[Message] = [Message(id=0, content="Первое сообщение в FastAPI")]

def nex_id() -> int:
    return max((maessage.id for maessage in messages_db), default= -1) +1

# Вспомогательная функция для получения индекса сообщения по ID
def get_index(message_id: int) -> int:
    for i, m in enumerate(messages_db):
        if m.id == message_id:
            return i
    return -1

#Получение всех сообщений
@app.get("/messages", response_model=list[Message])
async def get_messages_page() -> list[Message]:
    return messages_db

# Обработка создания сообщения
@app.post("/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message_form(content_new: MessageCreate) -> Message:
    message = Message(id= nex_id(), content= content_new.content)
    messages_db.append(message)
    return message

# Страница одного сообщения
@app.get("/messages/{message_id}", response_model=Message)
async def get_message_detail_page(message_id: int):
    idx = get_index(message_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return messages_db[idx]

#PATCH /messages/{message_id}
@app.patch("/messages/{message_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def update_message(message_id: int, content_new: MessageUpdate) -> Message:
    indx = get_index(message_id)
    if indx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    if content_new.content is not None:
        messages_db[indx].content = Message(content= content_new.content)
    return messages_db[indx]

#PUT /messages/{message_id}
@app.put("/messages/{message_id}", response_model=Message, status_code=status.HTTP_201_CREATED)
async def repalce_message(message_id: int, new_content = MessageCreate) -> Message:
    indx = get_index(message_id)
    if indx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    messages_db[indx] = Message(id= message_id, content= new_content.content)
    return messages_db[indx]

#DELETE /messages/{message_id}
@app.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: int):
    indx = get_index(message_id)
    if indx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    messages_db.pop(indx)








