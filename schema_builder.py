import json
import os
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.engine.url import URL
import database


def get_db_schema(connection_string=None, schema_name=None, **kwargs):
    """
    Connects to any SQLAlchemy-supported database and returns a JSON-like schema
    of all tables and their columns with data types.

    Args:
        connection_string: Full database URL (e.g., 'postgresql://user:pass@host:port/db')
        schema_name: Schema to inspect (for databases that support schemas like PostgreSQL)
        **kwargs: Alternative connection parameters (db_type, host, dbname, user, password, port)

    Returns:
        dict: Schema information including tables, columns, and constraints
    """
    # Create connection string if not provided
    if not connection_string:
        db_type = kwargs.get('db_type', 'postgresql')
        host = kwargs.get('db_host')
        dbname = kwargs.get('db_name')
        user = kwargs.get('db_username')
        password = kwargs.get('db_password')
        port = kwargs.get('db_port', 5432 if db_type == 'postgresql' else 3306)

        # Build connection string based on database type
        if db_type == 'mysql':
            driver = 'pymysql'  # or 'mysqlconnector'
            connection_string = f"mysql+{driver}://{user}:{password}@{host}:{port}/{dbname}"
        elif db_type == 'postgresql':
            driver = 'psycopg2'
            connection_string = f"postgresql+{driver}://{user}:{password}@{host}:{port}/{dbname}"
        elif db_type == 'sqlite':
            connection_string = f"sqlite:///{dbname}"
        elif db_type == 'mssql':
            driver = 'pymssql'
            connection_string = f"mssql+{driver}://{user}:{password}@{host}:{port}/{dbname}"
        elif db_type == 'oracle':
            driver = 'cx_oracle'
            connection_string = f"oracle+{driver}://{user}:{password}@{host}:{port}/{dbname}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    # Create engine and inspector
    engine = create_engine(connection_string)
    inspector = inspect(engine)

    # Get schema name based on database type
    if schema_name is None:
        db_dialect = engine.dialect.name
        if db_dialect == 'postgresql':
            schema_name = 'public'
        elif db_dialect == 'mysql':
            schema_name = engine.url.database
        # For SQLite, schema_name should be None

    # Get all table names
    table_names = inspector.get_table_names(schema=schema_name)

    schema = {}
    table_index = 1

    for table_name in table_names:
        # Get column information
        columns = inspector.get_columns(table_name, schema=schema_name)

        column_schema = {}
        for col in columns:
            # Convert SQLAlchemy type to string
            col_type = str(col['type'])
            column_schema[col['name']] = col_type

        schema[f"table_{table_index}"] = {
            "table_name": table_name,
            "columns": column_schema
        }

        table_index += 1

    # Collect constraints
    constraints = []

    for table_name in table_names:
        # Primary keys
        pk = inspector.get_pk_constraint(table_name, schema=schema_name)
        if pk and pk.get('constrained_columns'):
            for col in pk['constrained_columns']:
                constraints.append({
                    "type": "PRIMARY KEY",
                    "table": table_name,
                    "column": col,
                    "references": None
                })

        # Foreign keys
        fks = inspector.get_foreign_keys(table_name, schema=schema_name)
        for fk in fks:
            constrained_cols = fk.get('constrained_columns', [])
            referred_cols = fk.get('referred_columns', [])
            referred_table = fk.get('referred_table')

            for i, col in enumerate(constrained_cols):
                constraints.append({
                    "type": "FOREIGN KEY",
                    "table": table_name,
                    "column": col,
                    "references": {
                        "table": referred_table,
                        "column": referred_cols[i] if i < len(referred_cols) else None
                    }
                })

        # Unique constraints
        unique_constraints = inspector.get_unique_constraints(table_name, schema=schema_name)
        for uc in unique_constraints:
            for col in uc.get('column_names', []):
                constraints.append({
                    "type": "UNIQUE",
                    "table": table_name,
                    "column": col,
                    "references": None
                })

    schema["constraints"] = constraints

    # Close connection
    engine.dispose()

    return schema


if __name__ == "__main__":
    # Example 1: PostgreSQL (using database.py config)
    db_config = {
        "db_type": "postgresql",  # or "mysql", "sqlite", "mssql", "oracle"
        "host": database.host,
        "dbname": database.database_name,
        "user": database.username,
        "password": database.password,
        "port": database.port
    }

    # Example 2: MySQL configuration (uncomment to use)
    # db_config = {
    #     "db_type": "mysql",
    #     "host": "localhost",
    #     "dbname": "your_database",
    #     "user": "your_user",
    #     "password": "your_password",
    #     "port": 3306
    # }

    # Example 3: Using connection string directly
    # connection_string = "mysql+pymysql://user:password@localhost:3306/database"
    # schema = get_db_schema(connection_string=connection_string)

    # Generate schema
    schema = get_db_schema(**db_config)

    # Save schema to file
    db_name = db_config.get('dbname', 'database')
    output_file = f"db_schema_{db_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"✅ Database schema saved to: {os.path.abspath(output_file)}")
    print(f"📊 Found {len([k for k in schema.keys() if k.startswith('table_')])} tables")
    print(f"🔗 Found {len(schema.get('constraints', []))} constraints")
