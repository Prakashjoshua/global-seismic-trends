import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
csv_path = "raw_earthquake_data.csv"
df = pd.read_csv(csv_path)
USERNAME = "root"
PASSWORD = "root"   
HOST = "localhost"
PORT = "3306"
DATABASE = "guvi_project_01"
encoded_password = quote_plus(PASSWORD)
engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{encoded_password}@{HOST}:{PORT}/{DATABASE}"
)

try:
    with engine.connect() as conn:
        print("MySQL connection successful")
except Exception as e:
    print("MySQL connection failed")
    print(e)
    exit()

try:
    df.to_sql(
        name="earthquakes_raw",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )
    print("Data inserted into MySQL successfully")
except Exception as e:
    print("Error inserting data")
    print(e)
    exit()
print("COMPLETED SUCCESSFULLY")