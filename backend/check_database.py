import sqlite3
import json

def check_database():
    """Check what was stored in the database."""
    conn = sqlite3.connect('firewall_tool.db')
    cursor = conn.cursor()
    
    print("=== AUDIT SESSIONS ===")
    cursor.execute("SELECT * FROM audit_sessions")
    sessions = cursor.fetchall()
    for session in sessions:
        print(f"ID: {session[0]}, Name: {session[1]}, File: {session[4]}, Hash: {session[5]}")
        if session[6]:  # config_metadata
            metadata = json.loads(session[6])
            print(f"  Metadata: {metadata}")
    
    print("\n=== FIREWALL RULES ===")
    cursor.execute("SELECT * FROM firewall_rules")
    rules = cursor.fetchall()
    for rule in rules:
        print(f"Rule: {rule[2]} | Type: {rule[3]} | From: {rule[4]} -> To: {rule[5]} | Src: {rule[6]} -> Dst: {rule[7]} | Service: {rule[8]} | Action: {rule[9]} | Position: {rule[10]} | Disabled: {bool(rule[11])}")
    
    print("\n=== OBJECT DEFINITIONS ===")
    cursor.execute("SELECT * FROM object_definitions")
    objects = cursor.fetchall()
    for obj in objects:
        print(f"Object: {obj[3]} ({obj[2]}) | Value: {obj[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()
