import sqlite3

def run_migration():
    print("🚀 Starting End-to-End Data Migration Pipeline...")
    conn = sqlite3.connect('nhs_migration.db')
    cursor = conn.cursor()

    print("➔ Creating Target EPR Table and Quarantine Table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS target_modern_epr (
            nhs_number TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            dob TEXT,
            blood_type TEXT,
            last_visit TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migration_quarantine (
            patient_name TEXT,
            nhs_number TEXT,
            rejection_reason TEXT
        )
    ''')

    cursor.execute('DELETE FROM target_modern_epr')
    cursor.execute('DELETE FROM migration_quarantine')

    print("➔ Profiling data and routing invalid records to Quarantine...")
    cursor.execute('''
        INSERT INTO migration_quarantine (patient_name, nhs_number, rejection_reason)
        SELECT patient_name, nhs_number, 'MISSING_NHS_NUMBER'
        FROM staging_legacy_pas
        WHERE nhs_number IS NULL OR nhs_number = ''
    ''')

    print("➔ Executing complex ETL mapping and Deduplication logic...")
    
    cursor.execute('''
        INSERT INTO target_modern_epr (nhs_number, first_name, last_name, dob, blood_type, last_visit)
        WITH Deduplicated_Data AS (
            SELECT 
                nhs_number,
                SUBSTR(patient_name, 1, INSTR(patient_name, ' ') - 1) AS first_name,
                SUBSTR(patient_name, INSTR(patient_name, ' ') + 1) AS last_name,
                dob,
                blood_type,
                last_visit,
                ROW_NUMBER() OVER(
                    PARTITION BY nhs_number 
                    ORDER BY last_visit DESC
                ) as row_num
            FROM staging_legacy_pas
            WHERE nhs_number IS NOT NULL AND nhs_number != ''
        )
        SELECT nhs_number, first_name, last_name, dob, blood_type, last_visit
        FROM Deduplicated_Data
        WHERE row_num = 1;
    ''')

    conn.commit()

    print("\n MIGRATION COMPLETE! Generating Validation Report...")
    print("═" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM staging_legacy_pas")
    total_staged = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM migration_quarantine")
    total_quarantined = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM target_modern_epr")
    total_migrated = cursor.fetchone()[0]

    print(f"Total Staged Records (Legacy PAS):   {total_staged:,}")
    print(f"Records Quarantined (Bad Data):      {total_quarantined:,}")
    print(f"Records Successfully Migrated (EPR): {total_migrated:,}")
    
    duplicates_removed = total_staged - total_quarantined - total_migrated
    print(f"Duplicates Identified & Removed:     {duplicates_removed:,}")
    print("═" * 50)

    conn.close()

if __name__ == "__main__":
    run_migration()
    
    