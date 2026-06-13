import psycopg2
import pandas as pd

# Your old Supabase URL
supabase_url = "postgresql://postgres: CLLSupabase@db.urjluehagfemgflytzcn.supabase.co:5432/postgres"

# Your new Neon URL
neon_url = "postgresql://neondb_owner:npg_iUPJF5mhaB1q@ep-rapid-breeze-afdooow6.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

# Pull data from Supabase
supabase_conn = psycopg2.connect(supabase_url)
df = pd.read_sql_query("SELECT * FROM donations", supabase_conn)
supabase_conn.close()
print(f"✅ Pulled {len(df)} records from Supabase")

# Create tables & push to Neon
neon_conn = psycopg2.connect(neon_url)
cursor = neon_conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS donations (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        location TEXT NOT NULL,
        weight_lbs REAL,
        bins INTEGER,
        moveout TEXT,
        notes TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert donation records
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO donations (date, location, weight_lbs, bins, moveout, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (row['date'], row['location'], row['weight_lbs'],
          row.get('bins'), row.get('moveout'), row.get('notes')))

neon_conn.commit()
cursor.close()
neon_conn.close()
print(f"✅ Migrated {len(df)} records to Neon!")