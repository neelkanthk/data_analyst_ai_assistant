from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import models
from sqlalchemy import create_engine
from routes.models import *
from routes import connections, chat

app = FastAPI()

engine = models.engine

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connections.router)
app.include_router(chat.router)
