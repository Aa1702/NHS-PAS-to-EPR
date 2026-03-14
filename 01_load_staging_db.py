import sqlite3
import csv

conn = sqlite3.connect('nhs_migration.db')
cursor = conn.cursor()

print("Connected to database. Creating staging table...")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS staging_legacy_pas (
        patient_name TEXT,
        nhs_number TEXT,
        dob TEXT,
        blood_type TEXT,
        last_visit TEXT
    )
''')

cursor.execute('DELETE FROM staging_legacy_pas')

csv_file = 'legacy_pas_data.csv'
print(f"Loading data from {csv_file}...")

with open(csv_file, 'r', encoding='utf-8') as file:
    dr = csv.DictReader(file)
    to_db = [(i['patient_name'], i['nhs_number'], i['dob'], i['blood_type'], i['last_visit']) for i in dr]

cursor.executemany('''
    INSERT INTO staging_legacy_pas (patient_name, nhs_number, dob, blood_type, last_visit)
    VALUES (?, ?, ?, ?, ?)
''', to_db)

conn.commit()
conn.close()

print(f"Success! Inserted {len(to_db)} rows into the 'staging_legacy_pas' table.")