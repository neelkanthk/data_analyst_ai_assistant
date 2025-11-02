from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from config import database
from sqlalchemy import create_engine
import utilities
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime
from schema_builder import get_db_schema
import json

app = FastAPI()

# Database setup
engine = database.engine


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/connections", status_code=status.HTTP_200_OK)
def add_connection(request: AddConnectionRequest, db: Session = Depends(database.get_db)):
    new_connection = database.Connection(
        db_connection_name=request.name,
        db_name=request.database,
        db_type=request.type,
        db_host=request.host,
        db_port=request.port,
        db_username=request.username,
        db_password=request.password
    )
    db.add(new_connection)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "error": "Integrity Error",
                                "message": "Connection with same name already exists. Try using another connection name."
                            })

    db.refresh(new_connection)

    return AddConnectionResponse(
        success=True,
        message="New connection added successfully."
    )


@app.get('/connections', response_model=List[ConnectionListResponse])
def get_connections(db: Session = Depends(database.get_db)):
    connections = db.query(database.Connection).all()
    if connections is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"There are no connections created yet."
        })
    return connections


@app.get("/connections/{connection_id}", response_model=ConnectionDetailResponse)
def get_connection_detail(connection_id: int, db: Session = Depends(database.get_db)):
    connection = db.query(database.Connection).filter(database.Connection.id == connection_id).first()
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"Connection not found"
        })
    return connection


@app.delete("/connections/{connection_id}", response_model=ConnectionDeleteResponse)
def delete_connection(connection_id: int, db: Session = Depends(database.get_db)):
    connection = db.query(database.Connection).filter(database.Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "success": False,
            "message": f"Connection not found"
        })

    db.delete(connection)
    db.commit()
    return ConnectionDeleteResponse(
        success=True,
        message="Connection deleted successfully."
    )


@app.post("/connections/connect", response_model=ConnectionTestResponse)
def test_connection(request_payload: ConnectionTestRequest, db: Session = Depends(database.get_db)):
    connection_id = request_payload.connection_id
    connection = db.query(database.Connection).filter(database.Connection.id == connection_id).first()

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"Connection not found"
        })

    try:
        if connection.db_type == 'sqlite':
            connection_string = f"sqlite:///./{connection.db_name}.db"
            db_json_schema = get_db_schema(connection_string=connection_string, schema_name=None)
        else:
            db_config = {
                "db_type": connection.db_type,
                "db_host": connection.db_host,
                "db_port": connection.db_port,
                "db_username": connection.db_username,
                "db_password": connection.db_password,
                "db_name": connection.db_name
            }

            db_json_schema = get_db_schema(connection_string=None, schema_name=None, **db_config)

        connection.db_schema = json.dumps(db_json_schema, indent=2)
        db.add(connection)
        db.commit()
        # conn.close()
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed | {str(e)}"}


@app.post("/chat")
def chat(request_payload: ChatRequest, db: Session = Depends(database.get_db)):
    user_question = request_payload.question
    connection_id = request_payload.connection_id
    connection = db.query(database.Connection).filter(database.Connection.id == connection_id).first()

    # Step 1: Generate SQL from user query
    llm_response = utilities.generate_sql_from_user_query(user_question=user_question, db_schema=connection.db_schema)

    # Step 2: Extract SQL query from the LLM response
    sql_query = utilities.query_extractor(llm_response)

    # Step 3: Basic SQL validation
    is_safe_sql = utilities.is_safe_sql(sql_query)
    if not is_safe_sql:
        raise ValueError("Unsafe SQL detected.")

    # Connect with target database
    # Build connection string based on database type
    db_type = connection.db_type

    if db_type == 'mysql':
        driver = 'pymysql'  # or 'mysqlconnector'
        connection_string = f"mysql+{driver}://{connection.db_username}:{connection.db_password}@{connection.db_host}:{connection.db_port}/{connection.db_name}"
    elif db_type == 'postgresql':
        driver = 'psycopg2'
        connection_string = f"postgresql+{driver}://{connection.db_username}:{connection.db_password}@{connection.db_host}:{connection.db_port}/{connection.db_name}"
    elif db_type == 'sqlite':
        connection_string = f"sqlite:///./{connection.db_name}.db"
    elif db_type == 'mssql':
        driver = 'pymssql'
        connection_string = f"mssql+{driver}://{connection.db_username}:{connection.db_password}@{connection.db_host}:{connection.db_port}/{connection.db_name}"
    elif db_type == 'oracle':
        driver = 'cx_oracle'
        connection_string = f"oracle+{driver}://{connection.db_username}:{connection.db_password}@{connection.db_host}:{connection.db_port}/{connection.db_name}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    # Create engine
    engine = create_engine(connection_string)

    # Step 4: Execute query
    rows = []
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        # rows = [dict(r) for r in result]
        for row in result:
            rows.append(dict(row._mapping))

    return {"query": sql_query, "results": rows}
