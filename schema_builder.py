import psycopg2
import json
import os
import database


def get_db_schema(host, dbname, user, password, port=5432, schema_name="public"):
    """
    Connects to PostgreSQL and returns a JSON-like schema
    of all user tables (not system tables) and their columns with data types.
    """
    conn = psycopg2.connect(
        host=host,
        database=dbname,
        user=user,
        password=password,
        port=port
    )
    cursor = conn.cursor()

    # Fetch only user tables from the given schema
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """, (schema_name,))
    tables = [t[0] for t in cursor.fetchall()]

    schema = {}
    table_index = 1

    for table_name in tables:
        # Fetch column names and data types
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema_name, table_name))
        columns = cursor.fetchall()

        column_schema = {col: dtype for col, dtype in columns}

        schema[f"table_{table_index}"] = {
            "table_name": table_name,
            "columns": column_schema
        }

        table_index += 1

    # Fetch constraints only for these user tables
    cursor.execute("""
        SELECT
            tc.constraint_type,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM
            information_schema.table_constraints AS tc
        LEFT JOIN
            information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN
            information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE
            tc.table_schema = %s
            AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE')
        ORDER BY tc.table_name;
    """, (schema_name,))

    constraints = []
    for row in cursor.fetchall():
        constraint_type, table_name, column_name, foreign_table, foreign_column = row
        if table_name not in tables:
            # Skip system tables like pg_*
            continue
        constraints.append({
            "type": constraint_type,
            "table": table_name,
            "column": column_name,
            "references": {
                "table": foreign_table,
                "column": foreign_column
            } if foreign_table else None
        })

    schema["constraints"] = constraints

    cursor.close()
    conn.close()

    return schema


if __name__ == "__main__":
    # Update with your PostgreSQL credentials
    db_config = {
        "host": database.host,
        "dbname": database.database_name,
        "user": database.username,
        "password": database.password,
        "port": database.port
    }

    # Generate schema for the "public" schema only
    schema = get_db_schema(**db_config, schema_name="public")

    # Save schema to file
    output_file = "db_schema.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"✅ Cleaned database schema saved to: {os.path.abspath(output_file)}")
