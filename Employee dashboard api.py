# Required Modules for Employee Dashboard API
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import create_engine, MetaData, Table, select
import pandas as pd
import io
import urllib.parse
import decimal
import json

app = FastAPI()



DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "Demo_db",
    "user": "postgres",
    "password": "Lucky@1295"}

# Build connection string with encoding for special characters
user = urllib.parse.quote_plus(DB_CONFIG['user'])
password = urllib.parse.quote_plus(DB_CONFIG['password'])
conn_string = f"postgresql+psycopg2://{user}:{password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
engine = create_engine(conn_string)
metadata = MetaData()
metadata.reflect(bind=engine)


# Custom JSON encoder to handle Decimal values
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@app.get("/view-all-employees")
def view_all_employees():
    employee_table = metadata.tables['Employee_table']
    with engine.connect() as conn:
        result = conn.execute(select(employee_table.c.id, employee_table.c.name))
        employees = [{"id": row.id, "name": row.name} for row in result]
    return JSONResponse(content={"employees": employees})

@app.get("/view-all-departments")
def view_all_departments():
    department_table = metadata.tables['department']
    with engine.connect() as conn:
        result = conn.execute(select(department_table.c.id, department_table.c.name))
        departments = [{"id": row.id, "name": row.name} for row in result]
    return JSONResponse(content={"departments": departments})

@app.get("/employee-salary-details")
def employee_salary_details(download: bool = False):
    Employee_table = metadata.tables['Employee_table']
    salary_table = metadata.tables['employee_salary']
    with engine.connect() as conn:
        result = conn.execute(
            select(
                Employee_table.c.id.label("employee_id"),
                Employee_table.c.name.label("employee_name"),
                salary_table.c.salary
            ).join(salary_table, Employee_table.c.id == salary_table.c.id)
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    if download:
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
            "Content-Disposition": "attachment; filename=employee_salary_details.xlsx"
        })
    else:
        return JSONResponse(content=df.to_dict(orient="records"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
