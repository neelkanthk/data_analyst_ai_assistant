from fastapi import APIRouter, Depends, HTTPException, status
from config import database
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List
from schema_builder import get_db_schema
import json
from routes.models import *


router = APIRouter(prefix="/connections", tags=["Connections"])


@router.post("/", status_code=status.HTTP_200_OK)
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


@router.get('/', response_model=List[ConnectionListResponse])
def get_connections(db: Session = Depends(database.get_db)):
    connections = db.query(database.Connection).all()
    if connections is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"There are no connections created yet."
        })
    return connections


@router.get("/{connection_id}", response_model=ConnectionDetailResponse)
def get_connection_detail(connection_id: int, db: Session = Depends(database.get_db)):
    connection = db.query(database.Connection).filter(database.Connection.id == connection_id).first()
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"Connection not found"
        })
    return connection


@router.delete("/{connection_id}", response_model=ConnectionDeleteResponse)
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


@router.post("/connect", response_model=ConnectionTestResponse)
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
