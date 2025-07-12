#!/usr/bin/env python3
"""
Check the most recent audit to understand what was actually parsed.
"""

import sqlite3

def check_recent_audit():
    """Check the most recent audit session."""
    
    print("🔍 Checking Most Recent Audit")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get the most recent audit
        cursor.execute("""
            SELECT id, session_name, filename, status, start_time 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ No audit sessions found")
            return
        
        audit_id, session_name, filename, status, start_time = audit
        print(f"📋 Most Recent Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        print(f"   Status: {status}")
        print(f"   Time: {start_time}")
        
        # Check rules
        cursor.execute("""
            SELECT COUNT(*) FROM firewall_rules WHERE audit_session_id = ?
        """, (audit_id,))
        rule_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT rule_name, src, dst, service, action, is_disabled
            FROM firewall_rules 
            WHERE audit_session_id = ?
            ORDER BY position
            LIMIT 10
        """, (audit_id,))
        rules = cursor.fetchall()
        
        print(f"\n📊 Rules: {rule_count} total")
        if rules:
            print(f"   Sample rules:")
            for i, rule in enumerate(rules[:5]):
                status = "DISABLED" if rule[5] else "ENABLED"
                print(f"   {i+1}. {rule[0]}: {rule[1]} → {rule[2]} | {rule[3]} | {rule[4]} ({status})")
        
        # Check objects
        cursor.execute("""
            SELECT COUNT(*) FROM object_definitions WHERE audit_session_id = ?
        """, (audit_id,))
        object_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_session_id = ?
            ORDER BY name
        """, (audit_id,))
        objects = cursor.fetchall()
        
        print(f"\n📦 Objects: {object_count} total")
        if objects:
            used_count = sum(1 for obj in objects if obj[3] > 0)
            unused_count = sum(1 for obj in objects if obj[3] == 0)
            
            print(f"   Used: {used_count}")
            print(f"   Unused: {unused_count}")
            
            print(f"   All objects:")
            for i, obj in enumerate(objects):
                usage = f"Used in {obj[3]} rules" if obj[3] > 0 else "UNUSED"
                print(f"   {i+1}. {obj[0]} ({obj[1]}) = {obj[2]} | {usage}")
        
        conn.close()
        
        # Now check what the API returns
        print(f"\n🌐 Checking API Response...")
        import requests
        
        try:
            response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
            if response.status_code == 200:
                data = response.json()['data']
                summary = data['analysis_summary']
                
                print(f"📈 API Summary:")
                print(f"   Total Rules: {summary['total_rules']}")
                print(f"   Total Objects: {summary['total_objects']}")
                print(f"   Used Objects: {summary['used_objects_count']}")
                print(f"   Unused Objects: {summary['unused_objects_count']}")
                
                unused_objects = data.get('unusedObjects', [])
                print(f"\n📋 Unused Objects from API: {len(unused_objects)}")
                for i, obj in enumerate(unused_objects[:5]):
                    print(f"   {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')})")
                
                # Compare with database
                print(f"\n🔍 Database vs API Comparison:")
                print(f"   DB Rules: {rule_count} | API Rules: {summary['total_rules']}")
                print(f"   DB Objects: {object_count} | API Objects: {summary['total_objects']}")
                print(f"   DB Unused: {unused_count} | API Unused: {summary['unused_objects_count']}")
                
                if (rule_count == summary['total_rules'] and 
                    object_count == summary['total_objects'] and 
                    unused_count == summary['unused_objects_count']):
                    print(f"   ✅ Database and API are consistent")
                else:
                    print(f"   ❌ Database and API have discrepancies!")
                
            else:
                print(f"❌ API request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ API check failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")

if __name__ == "__main__":
    check_recent_audit()
