import psycopg2
import pandas as pd
import numpy as np

neon_url = "postgresql://neondb_owner:npg_iUPJF5mhaB1q@ep-rapid-breeze-afdooow6.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
df = pd.read_csv("/Users/kat/Downloads/donations.csv")

# Replace NaN with None so PostgreSQL gets NULL instead
df = df.where(pd.notnull(df), None)

conn = psycopg2.connect(neon_url)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO donations (date, location, weight_lbs, bins, moveout, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (row['date'], row['location'], row['weight_lbs'],
          int(row['bins']) if pd.notnull(row['bins']) else None,
          row['moveout'], row['notes']))

conn.commit()
cursor.close()
conn.close()
print(f"✅ Imported {len(df)} records to Neon!")