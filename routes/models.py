from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    question: str
    connection_id: int


class AddConnectionRequest(BaseModel):
    name: str
    database: str
    type: str
    host: Optional[str]
    port: Optional[str]
    username: Optional[str]
    password: Optional[str]


class AddConnectionResponse(BaseModel):
    success: bool
    message: str


class ConnectionListResponse(BaseModel):
    id: int
    db_connection_name: str
    db_type: str
    db_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ConnectionDetailResponse(BaseModel):
    id: int
    db_connection_name: str
    db_name: str
    db_type: str
    db_host: str
    db_port: int
    db_username: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ConnectionTestRequest(BaseModel):
    connection_id: int


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str


class ConnectionDeleteResponse(BaseModel):
    success: bool
    message: str
