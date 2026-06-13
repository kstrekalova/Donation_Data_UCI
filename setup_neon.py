import psycopg2

neon_url = "postgresql://neondb_owner:npg_iUPJF5mhaB1q@ep-rapid-breeze-afdooow6.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(neon_url)
cursor = conn.cursor()

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

conn.commit()
cursor.close()
conn.close()
print("✅ Tables created in Neon!")