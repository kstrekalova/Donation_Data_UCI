"""One-time script to import historical donation data into Supabase"""

import pandas as pd
import psycopg2
import toml

MONTH_MAP = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

# Load secrets
secrets = toml.load(".streamlit/secrets.toml")
conn = psycopg2.connect(secrets["DATABASE_URL"])
cursor = conn.cursor()

# Load Excel file — adjust filename if needed
df = pd.read_excel("../Donation_Data_UCI.xlsx")
print(f"Found {len(df)} rows to import...")

success = 0
for _, row in df.iterrows():
    try:
        year = int(row['Year'])
        month = MONTH_MAP.get(str(row['Month']).strip(), 1)
        date = f"{year:04d}-{month:02d}-01"

        # Handle "Not housing" flag — if asterisk present, append to notes
        not_housing = str(row['Not housing (*)']).strip() == '*' if pd.notna(row['Not housing (*)']) else False
        base_notes = str(row['Notes']) if pd.notna(row['Notes']) else ''
        notes = (base_notes + ' | Not Housing' if base_notes else 'Not Housing') if not_housing else (base_notes or None)

        cursor.execute('''
            INSERT INTO donations (date, location, weight_lbs, bins, moveout, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            date,
            row['Location'] if pd.notna(row['Location']) else None,
            float(row['Donation (lbs)']) if pd.notna(row['Donation (lbs)']) else None,
            str(row['Bins']) if pd.notna(row['Bins']) else None,
            str(row['Moveout (UG/G)']) if pd.notna(row['Moveout (UG/G)']) else None,
            notes,
        ))
        success += 1
    except Exception as e:
        print(f"⚠️ Row {_} failed: {e}")

conn.commit()
cursor.close()
conn.close()
print(f"✅ Imported {success}/{len(df)} records!")