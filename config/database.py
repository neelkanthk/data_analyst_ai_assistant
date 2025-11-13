from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# FastAPI app instance
app = FastAPI()

# Database setup
SQLITE_URL = "sqlite:///./db_assistant.db"
engine = create_engine(SQLITE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, server_default='false')
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    connections = relationship('Connection', back_populates="user", cascade='all, delete-orphan')


class Connection(Base):
    __tablename__ = 'connections'
    id = Column(Integer, primary_key=True, nullable=False)
    db_connection_name = Column(String, nullable=False, unique=True)  # A unique name of the database connection
    db_type = Column(String, nullable=False)  # Type of Datavase: mysql, postgresql, sqlite, mssql
    db_name = Column(String, nullable=False)  # Name of the database to connect with
    db_host = Column(String, nullable=True)  # Hostname or IP address of the database server
    db_port = Column(Integer, nullable=True)  # Port of the database server
    db_username = Column(String, nullable=True)  # Username of the database
    db_password = Column(String, nullable=True)  # Password of the database
    db_schema = Column(Text, nullable=True)  # Database schema in JSON format to be used in system prompt

    # ID of the user who created connection (for future use)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user = relationship('User', back_populates='connections')


# Create tables
Base.metadata.create_all(bind=engine)
