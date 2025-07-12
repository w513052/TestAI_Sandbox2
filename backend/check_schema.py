import sqlite3

def check_schema():
    """Check the database schema."""
    conn = sqlite3.connect('firewall_tool.db')
    cursor = conn.cursor()
    
    print("=== FIREWALL RULES TABLE SCHEMA ===")
    cursor.execute("PRAGMA table_info(firewall_rules)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"Column {col[0]}: {col[1]} ({col[2]})")
    
    print("\n=== SAMPLE RULE DATA ===")
    cursor.execute("SELECT * FROM firewall_rules LIMIT 1")
    rule = cursor.fetchone()
    if rule:
        for i, value in enumerate(rule):
            print(f"Column {i}: {value}")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
