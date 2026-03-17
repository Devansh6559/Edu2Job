# preprocess.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pandas as pd
import numpy as np

from models import User, db
from config import Config



engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

print(" Connected to database...")



users = session.query(User).all()

if not users:
    print("No user data found in DB!")
    exit()

data_rows = []

for u in users:
    data_rows.append({
        "degree": u.degree,
        "specialization": u.specialization,
        "cgpa": u.cgpa,
        "graduation_year": u.graduation_year,
        "university": u.university,
        "certifications": u.certifications
    })

df = pd.DataFrame(data_rows)
print("Raw Data Loaded:\n")
print(df.head())


df["degree"] = df["degree"].fillna("Unknown")
df["specialization"] = df["specialization"].fillna("Unknown")
df["university"] = df["university"].fillna("Unknown")
df["certifications"] = df["certifications"].fillna("None")

df["cgpa"] = df["cgpa"].fillna(df["cgpa"].mean())   # numeric mean fill
df["graduation_year"] = df["graduation_year"].fillna(df["graduation_year"].median())


encoders = {}

categorical_cols = ["degree", "specialization", "university", "certifications"]

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

print("\nLabel Encoding Completed.")



df["cgpa_norm"] = df["cgpa"] / 10



final_df = df[[
    "degree",
    "specialization",
    "cgpa_norm",
    "graduation_year"
]]

print("\n Final ML-ready Data:")
print(final_df.head())


final_df.to_csv("processed_data.csv", index=False)
print("\n Saved processed data to processed_data.csv")



print("\n Processed Vectors:")
for index, row in final_df.iterrows():
    vector = row.tolist()
    print(f"Processed Input: {vector}")
