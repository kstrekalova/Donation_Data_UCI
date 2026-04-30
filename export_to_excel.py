# One-time export script
from database import DonationDatabase
import pandas as pd

db = DonationDatabase()
df = db.get_all_donations()

# Clean it up a bit
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month_name'] = df['date'].dt.strftime('%B')
df['month_num'] = df['date'].dt.month

df.to_excel('donation_data.xlsx', index=False, sheet_name='Raw Data')
print('✅ Exported to donation_data.xlsx')