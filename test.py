from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("mysql+pymysql://root:Shivapspk123@localhost:3306/food_waste")

try:
    df = pd.read_sql("SELECT * FROM providers LIMIT 5;", engine)
    print(df)
except Exception as e:
    print("Error:", e)
