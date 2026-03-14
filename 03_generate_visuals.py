import sqlite3
import matplotlib.pyplot as plt

def generate_dashboard():
    print("📊 Generating Migration Summary Visuals...")
    
    conn = sqlite3.connect('nhs_migration.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM target_modern_epr")
    migrated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM migration_quarantine")
    quarantined = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM staging_legacy_pas")
    total_staged = cursor.fetchone()[0]
    
    duplicates = total_staged - migrated - quarantined
    conn.close()

    labels = ['Successfully Migrated', 'Quarantined (Missing Data)', 'Duplicates Removed']
    sizes = [migrated, quarantined, duplicates]
    colors = ['#2ca02c', '#d62728', '#ff7f0e'] 
    explode = (0.05, 0.1, 0.1)  

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140, textprops={'fontsize': 11})
    
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)

    ax.axis('equal')  
    plt.title('NHS PAS-to-EPR Data Migration Results', fontsize=14, weight='bold')
    
    output_file = 'migration_summary.png'
    plt.savefig(output_file, bbox_inches='tight')
    print(f"Success! Chart saved as '{output_file}'.")

if __name__ == "__main__":
    generate_dashboard()