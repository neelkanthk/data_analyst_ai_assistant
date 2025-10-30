from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text
import database
import utilities

app = FastAPI()

# Database setup
engine = database.engine


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
def chat(req: QueryRequest):
    user_query = req.query

    # Step 1: Generate SQL from user query
    llm_response = utilities.generate_sql_from_user_query(user_query)

    # Step 2: Extract SQL query from the LLM response
    sql_query = utilities.query_extractor(llm_response)

    # Step 3: Basic SQL validation
    is_safe_sql = utilities.is_safe_sql(sql_query)
    if not is_safe_sql:
        raise ValueError("Unsafe SQL detected.")

    # Step 4: Execute query
    rows = []
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        # rows = [dict(r) for r in result]
        for row in result:
            rows.append(dict(row._mapping))

    return {"sql": sql_query, "data": rows}
