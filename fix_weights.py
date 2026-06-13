import psycopg2
import pandas as pd

neon_url = "postgresql://neondb_owner:npg_iUPJF5mhaB1q@ep-rapid-breeze-afdooow6.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

df = pd.read_csv("/Users/kat/Downloads/donations.csv") 

# Only update rows that actually have weight values
df_with_weight = df[df['weight_lbs'].notna()]

conn = psycopg2.connect(neon_url)
cursor = conn.cursor()

updated = 0
for _, row in df_with_weight.iterrows():
    cursor.execute(
        "UPDATE donations SET weight_lbs = %s WHERE id = %s",
        (float(row['weight_lbs']), int(row['id']))
    )
    updated += cursor.rowcount

conn.commit()
cursor.close()
conn.close()
print(f"Updated {updated} rows with weight data!")