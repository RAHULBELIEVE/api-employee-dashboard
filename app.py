import urllib.parse
from sqlalchemy import create_engine, inspect

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "Demo_db",
    "user": "postgres",
    "password": "Lucky@1295"}


def get_connection_string(config):
    user = urllib.parse.quote_plus(config['user'])
    password = urllib.parse.quote_plus(config['password'])
    return f"postgresql+psycopg2://{user}:{password}@{config['host']}:{config['port']}/{config['dbname']}"

def fetch_tables_and_schemas():
    conn_string = get_connection_string(DB_CONFIG)
    engine = create_engine(conn_string)

    inspector = inspect(engine)

    print("Fetching all tables in the database:")
    tables = inspector.get_table_names()
    for table in tables:
        print(f"\nTable: {table}")
        columns = inspector.get_columns(table)
        print("Schema:")
        for column in columns:
            print(f"  {column['name']} - {column['type']}")

    engine.dispose()

if __name__ == "__main__":
    fetch_tables_and_schemas()
