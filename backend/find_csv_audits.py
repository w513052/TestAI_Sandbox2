#!/usr/bin/env python3
"""
Find CSV audits in the database.
"""

import sqlite3

def find_csv_audits():
    """Find all CSV audits."""
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get all audits
        cursor.execute('''
            SELECT id, session_name, filename 
            FROM audit_sessions 
            ORDER BY id DESC
        ''')
        
        all_audits = cursor.fetchall()
        
        print("🔍 ALL AUDITS IN DATABASE:")
        csv_found = False
        
        for audit_id, session_name, filename in all_audits:
            file_ext = filename.split('.')[-1].lower() if '.' in filename else 'no_ext'
            
            if file_ext == 'csv':
                print(f"   📊 CSV: {audit_id} - {filename}")
                csv_found = True
            elif file_ext == 'txt':
                print(f"   📝 SET: {audit_id} - {filename}")
            elif file_ext == 'xml':
                print(f"   📄 XML: {audit_id} - {filename}")
            else:
                print(f"   ❓ {file_ext.upper()}: {audit_id} - {filename}")
        
        if not csv_found:
            print("\n❌ NO CSV FILES FOUND!")
            print("   You may have uploaded:")
            print("   - SET format (.txt) files")
            print("   - XML format (.xml) files")
            print("   - But no CSV format (.csv) files")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    find_csv_audits()
