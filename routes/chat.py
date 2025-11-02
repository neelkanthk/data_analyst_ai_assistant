from fastapi import APIRouter, Depends, HTTPException, status
from config import database
from sqlalchemy.orm import Session
from routes.models import *
import utilities
from sqlalchemy import create_engine
from sqlalchemy import text


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
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
