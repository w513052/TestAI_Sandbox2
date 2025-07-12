#!/usr/bin/env python3
"""
Debug the complex file upload to understand parsing discrepancies.
"""

import requests
import sqlite3
import json

def debug_recent_upload():
    """Debug the most recent upload to understand parsing issues."""
    
    print("🔍 DEBUGGING COMPLEX FILE UPLOAD")
    print("=" * 50)
    
    try:
        # Get the most recent audit
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
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
        
        # Get detailed rule information
        cursor.execute("""
            SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ?
        """, (audit_id,))
        total_rules = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT rule_name, rule_type, src_zone, dst_zone, src, dst, service, action, position, is_disabled
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
        """, (audit_id,))
        rules = cursor.fetchall()
        
        print(f"\n📊 Rules Analysis:")
        print(f"   Total Rules Found: {total_rules}")
        
        if rules:
            enabled_rules = [r for r in rules if not r[9]]
            disabled_rules = [r for r in rules if r[9]]
            
            print(f"   Enabled Rules: {len(enabled_rules)}")
            print(f"   Disabled Rules: {len(disabled_rules)}")
            
            print(f"\n📋 Sample Rules:")
            for i, rule in enumerate(rules[:10]):
                status = "DISABLED" if rule[9] else "ENABLED"
                print(f"   {i+1}. {rule[0]} | {rule[4]} → {rule[5]} | {rule[6]} | {rule[7]} ({status})")
        
        # Get detailed object information
        cursor.execute("""
            SELECT COUNT(*) FROM object_definitions WHERE audit_id = ?
        """, (audit_id,))
        total_objects = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT object_type, COUNT(*) 
            FROM object_definitions 
            WHERE audit_id = ?
            GROUP BY object_type
        """, (audit_id,))
        object_counts = cursor.fetchall()
        
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_id = ?
            ORDER BY object_type, name
        """, (audit_id,))
        objects = cursor.fetchall()
        
        print(f"\n📦 Objects Analysis:")
        print(f"   Total Objects Found: {total_objects}")
        
        for obj_type, count in object_counts:
            print(f"   {obj_type.title()} Objects: {count}")
        
        # Analyze object usage
        used_objects = [obj for obj in objects if obj[3] > 0]
        unused_objects = [obj for obj in objects if obj[3] == 0]
        
        print(f"   Used Objects: {len(used_objects)}")
        print(f"   Unused Objects: {len(unused_objects)}")
        
        # Show all objects with usage
        print(f"\n📋 All Objects:")
        address_objects = [obj for obj in objects if obj[1] == 'address']
        service_objects = [obj for obj in objects if obj[1] == 'service']
        
        print(f"   Address Objects ({len(address_objects)}):")
        for i, obj in enumerate(address_objects):
            usage = f"Used in {obj[3]} rules" if obj[3] > 0 else "UNUSED"
            print(f"      {i+1}. {obj[0]} = {obj[2]} | {usage}")
        
        if service_objects:
            print(f"   Service Objects ({len(service_objects)}):")
            for i, obj in enumerate(service_objects):
                usage = f"Used in {obj[3]} rules" if obj[3] > 0 else "UNUSED"
                print(f"      {i+1}. {obj[0]} = {obj[2]} | {usage}")
        
        conn.close()
        
        # Get API analysis results
        print(f"\n🌐 API Analysis Results:")
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
                
                # Show analysis categories
                categories = {
                    'unusedRules': 'Unused Rules',
                    'duplicateRules': 'Duplicate Rules',
                    'shadowedRules': 'Shadowed Rules',
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
                        print(f"   {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')}) = {obj.get('value', 'N/A')}")
                
                # Compare with expected values
                print(f"\n🎯 Expected vs Actual Comparison:")
                expected = {
                    "Total Address Objects": 17,
                    "Unused Address Objects": 2,
                    "Total Security Policies": 17
                }
                
                actual = {
                    "Total Address Objects": len(address_objects),
                    "Unused Address Objects": len([obj for obj in address_objects if obj[3] == 0]),
                    "Total Security Policies": summary['total_rules']
                }
                
                print(f"   Expected breakdown:")
                print(f"      Total Address Objects: 17 (12 original + 5 redundant)")
                print(f"      Unused Address Objects: 2 (Backup-Server-01, Monitoring-Host-01)")
                print(f"      Total Security Policies: 17 (10 original + 5 redundant + 2 duplicate)")
                
                print(f"   Actual results:")
                for key in expected:
                    expected_val = expected[key]
                    actual_val = actual[key]
                    status = "✅" if actual_val == expected_val else "❌"
                    print(f"      {key}: Expected={expected_val}, Actual={actual_val} {status}")
                
                # Identify specific discrepancies
                print(f"\n🔍 Discrepancy Analysis:")
                
                if actual["Total Address Objects"] != expected["Total Address Objects"]:
                    print(f"   📦 Address Objects Mismatch:")
                    print(f"      Expected 17 address objects, found {actual['Total Address Objects']}")
                    print(f"      This suggests the XML structure might be different than expected")
                    print(f"      Check if objects are in a different location or format")
                
                if actual["Unused Address Objects"] != expected["Unused Address Objects"]:
                    print(f"   🔍 Unused Objects Mismatch:")
                    print(f"      Expected 2 unused objects (Backup-Server-01, Monitoring-Host-01)")
                    print(f"      Found {actual['Unused Address Objects']} unused objects")
                    print(f"      Check object names and rule references")
                
                if actual["Total Security Policies"] != expected["Total Security Policies"]:
                    print(f"   📋 Rules Mismatch:")
                    print(f"      Expected 17 security policies, found {actual['Total Security Policies']}")
                    print(f"      This suggests rules might be in a different XML section")
                    print(f"      Check if rules are in NAT, QoS, or other sections")
                
                return audit_id
                
            else:
                print(f"❌ API request failed: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ API check failed: {str(e)}")
            return None
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def suggest_fixes():
    """Suggest potential fixes for parsing discrepancies."""
    
    print(f"\n🔧 POTENTIAL FIXES:")
    print("=" * 30)
    
    print(f"1. **XML Structure Issues:**")
    print(f"   - Objects might be in different XML sections")
    print(f"   - Rules might be in NAT, QoS, or other rulebase sections")
    print(f"   - Check if the file uses a different XML schema")
    
    print(f"\n2. **Object Naming Issues:**")
    print(f"   - Object names might have different casing")
    print(f"   - Objects might be referenced with prefixes/suffixes")
    print(f"   - Check for object groups or nested references")
    
    print(f"\n3. **Rule Reference Issues:**")
    print(f"   - Rules might reference objects indirectly")
    print(f"   - Object usage might be in different rule fields")
    print(f"   - Check for object groups that contain the objects")
    
    print(f"\n4. **Parser Limitations:**")
    print(f"   - Parser might not handle all XML variations")
    print(f"   - Streaming parser vs regular parser differences")
    print(f"   - Check for XML namespaces or attributes")

if __name__ == "__main__":
    audit_id = debug_recent_upload()
    
    if audit_id:
        suggest_fixes()
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Check the actual XML file structure")
        print(f"   2. Verify object names match exactly")
        print(f"   3. Check if rules reference objects correctly")
        print(f"   4. Consider updating the parser for this XML format")
    else:
        print(f"\n❌ Could not debug - no recent upload found")
