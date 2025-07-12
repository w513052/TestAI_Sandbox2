#!/usr/bin/env python3
"""
Verify the recent audit data to understand the parsing issue.
"""

import sqlite3
import requests

def verify_recent_audit():
    """Verify the most recent audit data."""
    
    print("🔍 Verifying Recent Audit Data")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get the most recent audit
        cursor.execute("""
            SELECT id, session_name, filename, start_time 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ No audit sessions found")
            return
        
        audit_id, session_name, filename, start_time = audit
        print(f"📋 Most Recent Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        print(f"   Time: {start_time}")
        
        # Check rules
        cursor.execute("SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ?", (audit_id,))
        rule_count = cursor.fetchone()[0]

        # Check objects
        cursor.execute("SELECT COUNT(*) FROM object_definitions WHERE audit_id = ?", (audit_id,))
        object_count = cursor.fetchone()[0]
        
        print(f"\n📈 Database Counts:")
        print(f"   Rules: {rule_count}")
        print(f"   Objects: {object_count}")
        
        # Get detailed object information
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions
            WHERE audit_id = ?
            ORDER BY name
        """, (audit_id,))
        objects = cursor.fetchall()
        
        if objects:
            used_objects = [obj for obj in objects if obj[3] > 0]
            unused_objects = [obj for obj in objects if obj[3] == 0]
            
            print(f"\n📦 Object Analysis:")
            print(f"   Total Objects: {len(objects)}")
            print(f"   Used Objects: {len(used_objects)}")
            print(f"   Unused Objects: {len(unused_objects)}")
            
            print(f"\n📋 Detailed Object List:")
            for i, obj in enumerate(objects):
                usage_status = f"Used in {obj[3]} rules" if obj[3] > 0 else "UNUSED"
                print(f"   {i+1}. {obj[0]} ({obj[1]}) = '{obj[2]}' | {usage_status}")
        
        # Get rule information if any
        if rule_count > 0:
            cursor.execute("""
                SELECT rule_name, src, dst, service, action, is_disabled, position
                FROM firewall_rules
                WHERE audit_id = ?
                ORDER BY position
            """, (audit_id,))
            rules = cursor.fetchall()
            
            print(f"\n📊 Rules Analysis:")
            enabled_rules = [r for r in rules if not r[5]]
            disabled_rules = [r for r in rules if r[5]]
            
            print(f"   Total Rules: {len(rules)}")
            print(f"   Enabled Rules: {len(enabled_rules)}")
            print(f"   Disabled Rules: {len(disabled_rules)}")
            
            print(f"\n📋 Sample Rules:")
            for i, rule in enumerate(rules[:10]):
                status = "DISABLED" if rule[5] else "ENABLED"
                print(f"   {i+1}. {rule[0]}: {rule[1]} → {rule[2]} | {rule[3]} | {rule[4]} ({status})")
        
        conn.close()
        
        # Now check API response
        print(f"\n🌐 API Response Check:")
        try:
            response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
            if response.status_code == 200:
                data = response.json()['data']
                summary = data['analysis_summary']
                
                print(f"📈 API Analysis Summary:")
                print(f"   Total Rules: {summary['total_rules']}")
                print(f"   Total Objects: {summary['total_objects']}")
                print(f"   Used Objects: {summary['used_objects_count']}")
                print(f"   Unused Objects: {summary['unused_objects_count']}")
                
                # Check analysis categories
                categories = {
                    'duplicateRules': 'Duplicate Rules',
                    'shadowedRules': 'Shadowed Rules',
                    'unusedRules': 'Unused Rules',
                    'overlappingRules': 'Overlapping Rules',
                    'unusedObjects': 'Unused Objects'
                }
                
                print(f"\n📋 Analysis Categories:")
                for key, name in categories.items():
                    items = data.get(key, [])
                    print(f"   {name}: {len(items)} items")
                
                # Show unused objects details
                unused_objects_api = data.get('unusedObjects', [])
                if unused_objects_api:
                    print(f"\n📦 Unused Objects from API:")
                    for i, obj in enumerate(unused_objects_api):
                        print(f"   {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')}) - {obj.get('description', 'N/A')}")
                
                # Compare database vs API
                print(f"\n🔍 Database vs API Comparison:")
                db_unused = len([obj for obj in objects if obj[3] == 0])
                api_unused = summary['unused_objects_count']
                
                print(f"   Rules: DB={rule_count}, API={summary['total_rules']} {'✅' if rule_count == summary['total_rules'] else '❌'}")
                print(f"   Objects: DB={object_count}, API={summary['total_objects']} {'✅' if object_count == summary['total_objects'] else '❌'}")
                print(f"   Unused: DB={db_unused}, API={api_unused} {'✅' if db_unused == api_unused else '❌'}")
                
                return audit_id, rule_count, object_count, db_unused
                
            else:
                print(f"❌ API request failed: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ API check failed: {str(e)}")
            return None
        
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        return None

if __name__ == "__main__":
    result = verify_recent_audit()
    if result:
        audit_id, rules, objects, unused = result
        print(f"\n✅ Verification complete for audit {audit_id}")
        print(f"   Found: {rules} rules, {objects} objects, {unused} unused")
        
        # Based on user's expected numbers
        expected_rules = 10
        expected_objects = 10
        expected_unused = 8
        expected_used = 2
        
        print(f"\n🎯 Expected vs Actual:")
        print(f"   Rules: Expected={expected_rules}, Actual={rules} {'✅' if rules == expected_rules else '❌'}")
        print(f"   Objects: Expected={expected_objects}, Actual={objects} {'✅' if objects == expected_objects else '❌'}")
        print(f"   Unused: Expected={expected_unused}, Actual={unused} {'✅' if unused == expected_unused else '❌'}")
        
        if rules != expected_rules or objects != expected_objects or unused != expected_unused:
            print(f"\n🚨 DISCREPANCY FOUND!")
            print(f"   The parsing or analysis logic needs investigation")
        else:
            print(f"\n✅ Numbers match expectations!")
    else:
        print(f"\n❌ Verification failed")
