from fastapi import APIRouter, Depends, HTTPException, status
from config import database
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session
from typing import List
import json
from routes.models import *
from repositories import ConnectionRepository


router = APIRouter(prefix="/connections", tags=["Connections"])


@router.post("/", status_code=status.HTTP_200_OK)
def add_connection(request: AddConnectionRequest, db: Session = Depends(database.get_db)):
    data = request.model_dump(exclude_unset=True)
    repository = ConnectionRepository(db)
    try:
        repository.add(data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "error": "Integrity Error",
                                "message": "Connection with same name already exists. Try using another connection name."
                            })

    return AddConnectionResponse(
        success=True,
        message="New connection added successfully."
    )


@router.get('/', response_model=List[ConnectionListResponse])
def get_connections(db: Session = Depends(database.get_db)):
    repository = ConnectionRepository(db)
    try:
        connections = repository.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"Connection not found"
        })
    return connections


@router.get("/{connection_id}", response_model=ConnectionDetailResponse)
def get_connection_detail(connection_id: int, db: Session = Depends(database.get_db)):
    repository = ConnectionRepository(db)
    try:
        connection = repository.find(connection_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"Connection not found"
        })
    return connection


@router.delete("/{connection_id}", response_model=ConnectionDeleteResponse)
def delete_connection(connection_id: int, db: Session = Depends(database.get_db)):
    repository = ConnectionRepository(db)
    try:
        repository.delete(connection_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "success": False,
            "message": f"Connection not found"
        })
    return ConnectionDeleteResponse(
        success=True,
        message="Connection deleted successfully."
    )


@router.post("/connect", response_model=ConnectionTestResponse)
def establish_connection(request_payload: ConnectionTestRequest, db: Session = Depends(database.get_db)):
    connection_id = request_payload.connection_id
    repository = ConnectionRepository(db)
    try:
        repository.connect(connection_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": "Not Found",
            "message": f"Connection not found"
        })
    except Exception as e:
        return {"success": False, "message": f"Connection failed | {str(e)}"}

    return {"success": True, "message": "Connection successful"}
