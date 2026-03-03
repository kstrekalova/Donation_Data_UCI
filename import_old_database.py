"""Import data from existing spreadsheets into the database"""

import pandas as pd
import sqlite3
import config

def import_from_excel(excel_file):
    """Import data from an Excel file"""
    print(f"Reading {excel_file}...")
    
    # Read the spreadsheet
    df = pd.read_excel(excel_file)
    
    # Normalize column names: lowercase and strip whitespace
    df.columns = df.columns.str.strip().str.lower()
    
    print(f"Found {len(df)} records")
    print(f"Original columns: {df.columns.tolist()}\n")
    
    # Map old columns to new schema
    column_mapping = {
        'location': 'location',
        'donation (lbs)': 'weight_lbs',
        'bins': 'bins',
        'moveout (ug/g)': 'moveout',
        'not housing (*)': 'not_housing_flag',
        'notes': 'notes',
    }
    
    # Rename columns (only ones that exist)
    existing_mappings = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_mappings)
    
    # ========================================
    # DATE CONVERSION
    # ========================================
    month_mapping = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    # Convert month column - handle BOTH text and numbers
    def convert_month(val):
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return int(val)
        val_str = str(val).strip().lower()
        return month_mapping.get(val_str, None)
    
    df['month_num'] = df['month'].apply(convert_month)
    
    # Create dates
    valid_rows = df[df['month_num'].notna()].copy()
    valid_rows['date'] = pd.to_datetime(
        valid_rows['year'].astype(int).astype(str) + '-' + 
        valid_rows['month_num'].astype(int).astype(str) + '-01'
    ).dt.strftime('%Y-%m-%d')
    
    df.loc[valid_rows.index, 'date'] = valid_rows['date']
    
    # Report on skipped rows
    rows_before = len(df)
    df = df.dropna(subset=['date'])
    rows_after = len(df)
    
    if rows_before > rows_after:
        print(f"⚠️  Skipped {rows_before - rows_after} rows with missing dates")
        print(f"✓ Continuing with {rows_after} valid records...\n")
    
    # Combine notes
    if 'not_housing_flag' in df.columns:
        df['notes'] = df.apply(
            lambda row: (
                f"{row.get('notes', '')} | Not Housing: {row['not_housing_flag']}" 
                if pd.notna(row['not_housing_flag'])
                else row.get('notes')
            ),
            axis=1
        )
    
    # Clean location
    if 'location' in df.columns:
        df['location'] = df['location'].str.strip()
    
    # Keep only schema columns
    schema_columns = ['date', 'location', 'weight_lbs', 'bins', 'moveout', 'notes']
    df_clean = df[[col for col in schema_columns if col in df.columns]]
    
    # Show preview
    print("=" * 60)
    print("PREVIEW - First 5 rows:")
    print("=" * 60)
    print(df_clean.head().to_string())
    print(f"\nData types: {df_clean.dtypes.to_dict()}")
    print("=" * 60)
    
    # Insert into database
    conn = sqlite3.connect(config.DATABASE_PATH)
    df_clean.to_sql('donations', conn, if_exists='append', index=False)
    conn.close()
    
    print(f"\n✅ SUCCESS! Imported {len(df_clean)} records to database!\n")

if __name__ == "__main__":
    import_from_excel('/Users/kat/Documents/projects/CLLProjects/Donation_Data_UCI/Donation_Data_UCI.xlsx')