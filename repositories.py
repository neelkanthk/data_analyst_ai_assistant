from sqlalchemy.orm import Session
from config.database import Connection
from sqlalchemy.exc import IntegrityError, NoResultFound
from schema_builder import get_db_schema
import json


class ConnectionRepository():
    def __init__(self, db: Session):
        self.db = db

    def add(self, data) -> Connection:

        connection = Connection(
            db_connection_name=data['name'],
            db_name=data['database'],
            db_type=data['type'],
            db_host=data['host'],
            db_port=data['port'],
            db_username=data['username'],
            db_password=data['password']
        )
        self.db.add(connection)

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise IntegrityError

        self.db.refresh(connection)
        return connection

    def find(self, id: int) -> Connection:
        try:
            connection = self.db.query(Connection).filter(Connection.id == id).first()
            if not connection:
                raise NoResultFound
        except Exception as e:
            raise Exception
        return connection

    def all(self):
        try:
            connections = self.db.query(Connection).all()
            if not connections:
                raise NoResultFound
        except Exception as e:
            raise Exception
        return connections

    def delete(self, id) -> bool:
        try:
            connection = self.db.query(Connection).filter(Connection.id == id).first()
            if not connection:
                raise NoResultFound

            self.db.delete(connection)
            self.db.commit()
        except Exception as e:
            raise Exception
        return True

    def connect(self, id) -> bool:
        try:
            connection = self.db.query(Connection).filter(Connection.id == id).first()
            if not connection:
                raise NoResultFound
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
            self.db.add(connection)
            self.db.commit()
            return True
        except Exception as e:
            pass
