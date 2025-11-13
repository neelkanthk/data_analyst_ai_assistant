from fastapi import APIRouter, Depends, HTTPException, status
from config import database
from sqlalchemy.orm import Session
from routes.models import *
import utilities
from sqlalchemy import create_engine
from sqlalchemy import text
from providers.client import InferenceProviderClient
from providers.providertypes import InferenceProviderType
from providers.factory import InferenceProviderFactory
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
def chat(request_payload: ChatRequest, db: Session = Depends(database.get_db)):
    user_question = request_payload.question  # Used in user prompt
    connection_id = request_payload.connection_id
    connection = db.query(database.Connection).filter(database.Connection.id == connection_id).first()
    db_schema = connection.db_schema  # Used in system prompt

    # Step 1: Generate SQL from user query
    system_prompt = f"""
            You are a highly intelligent SQL query generator. Your role is to:
            1. Analyze the natural language query carefully
            2. Understand the database schema structure
            3. Identify relevant tables, columns, and relationships
            4. Generate correct, optimized SQL queries
            5. Follow standard SQL syntax
            6. Only generate SQL queries that are safe to run (i.e., only SELECT statements)

            Key Guidelines:
            - Create SQL which must run on {connection.db_type} database
            - Use only columns and tables present in the schema
            - Pay attention to data types and constraints
            - Consider foreign key relationships for joins
            - Optimize for performance when possible
            - Return only the SQL query without reasoning, additional text or formatting
            - SQL query must be syntactically correct ans safe to execute
            - Enclose the SQL query within <sql> and </sql> delimiters

            Use following Database Schema to create the SQL query: {db_schema}
        """

    # provider = InferenceProviderFactory.create(
    #     InferenceProviderType.GEMINI, api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

    provider = InferenceProviderFactory.create(
        InferenceProviderType.BEDROCK, api_key=os.getenv("AWS_BEDROCK_API_KEY"), base_url=os.getenv("AWS_BEDROCK_BASE_URL"))

    client = InferenceProviderClient(provider)

    # Step 1: Use AI service to convert question in Natural Language to SQL
    response = client.ask(model_name="openai.gpt-oss-20b-1:0", system_prompt=system_prompt, user_prompt=user_question)
    print(response)

    # Step 2: Extract SQL query from the LLM response
    sql_query = utilities.query_extractor(response)
    print(sql_query)
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
