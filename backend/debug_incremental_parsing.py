#!/usr/bin/env python3
"""
Debug why the incremental parsing is not working.
"""

def test_incremental_parsing_directly():
    """Test the incremental parsing function directly."""
    
    print("🔍 TESTING INCREMENTAL PARSING DIRECTLY")
    print("=" * 50)
    
    try:
        from src.utils.parse_config import parse_set_config
        
        # Test with a simple incremental format
        test_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32
set address Server-DB-01 ip-netmask 192.168.10.20/32

set security rules "Allow-Web-Access" from trust
set security rules "Allow-Web-Access" to untrust
set security rules "Allow-Web-Access" source Server-Web-01
set security rules "Allow-Web-Access" destination any
set security rules "Allow-Web-Access" service service-http
set security rules "Allow-Web-Access" action allow

set security rules "Allow-DB-Access" from trust
set security rules "Allow-DB-Access" to dmz
set security rules "Allow-DB-Access" source Server-DB-01
set security rules "Allow-DB-Access" destination any
set security rules "Allow-DB-Access" service service-mysql
set security rules "Allow-DB-Access" action allow"""
        
        print(f"📋 Test Content:")
        lines = test_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                print(f"   {i+1:2d}. {line}")
        
        print(f"\n🧪 Calling parse_set_config...")
        rules_data, objects_data, metadata = parse_set_config(test_content)
        
        print(f"\n📊 Parsing Results:")
        print(f"   Rules parsed: {len(rules_data)}")
        print(f"   Objects parsed: {len(objects_data)}")
        
        print(f"\n📋 Rules Found:")
        for i, rule in enumerate(rules_data):
            print(f"   {i+1}. {rule['rule_name']}")
            print(f"      {rule['src_zone']} → {rule['dst_zone']} | {rule['src']} → {rule['dst']} | {rule['service']} | {rule['action']}")
        
        print(f"\n📦 Objects Found:")
        for i, obj in enumerate(objects_data):
            print(f"   {i+1}. {obj['name']} = {obj['value']}")
        
        # Expected: 2 rules (Allow-Web-Access, Allow-DB-Access), 2 objects
        expected_rules = 2
        expected_objects = 2
        
        print(f"\n🎯 Expected vs Actual:")
        print(f"   Rules: Expected={expected_rules}, Actual={len(rules_data)} {'✅' if len(rules_data) == expected_rules else '❌'}")
        print(f"   Objects: Expected={expected_objects}, Actual={len(objects_data)} {'✅' if len(objects_data) == expected_objects else '❌'}")
        
        if len(rules_data) == expected_rules:
            print(f"\n✅ Incremental parsing is working correctly!")
            return True
        else:
            print(f"\n❌ Incremental parsing is NOT working!")
            print(f"   Expected 2 consolidated rules, got {len(rules_data)}")
            return False
        
    except Exception as e:
        print(f"❌ Direct test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def debug_why_not_working():
    """Debug why the incremental parsing is not working in the uploaded file."""
    
    print(f"\n🔍 DEBUGGING WHY INCREMENTAL PARSING NOT WORKING")
    print("=" * 60)
    
    try:
        import sqlite3
        
        # Get the most recent audit
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_name, filename 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ No audit sessions found")
            return
        
        audit_id, session_name, filename = audit
        print(f"📋 Most Recent Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        # Check if this is the incremental test file
        if "Incremental" not in session_name:
            print(f"⚠️  This is not the incremental test file!")
            print(f"   The issue might be with a different file format")
            return
        
        # Get sample rules to see the pattern
        cursor.execute("""
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action, raw_xml
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
            LIMIT 10
        """, (audit_id,))
        
        rules = cursor.fetchall()
        
        print(f"\n📋 Sample Rules from Database:")
        for i, rule in enumerate(rules):
            rule_name, src_zone, dst_zone, src, dst, service, action, raw_xml = rule
            print(f"   {i+1}. {rule_name}")
            print(f"      Zones: {src_zone} → {dst_zone}")
            print(f"      Objects: {src} → {dst}")
            print(f"      Service: {service}")
            print(f"      Action: {action}")
            print(f"      Raw: {raw_xml[:100]}...")
            print()
        
        conn.close()
        
        # Check if rules have the same name but different attributes
        rule_names = [rule[0] for rule in rules]
        unique_names = set(rule_names)
        
        print(f"📊 Rule Name Analysis:")
        print(f"   Total rules: {len(rules)}")
        print(f"   Unique rule names: {len(unique_names)}")
        print(f"   Unique names: {list(unique_names)[:5]}")
        
        if len(unique_names) < len(rules):
            print(f"\n🚨 PROBLEM IDENTIFIED:")
            print(f"   Multiple rules with same name found!")
            print(f"   This means incremental parsing is NOT consolidating rules")
            print(f"   Each set command is still being stored as a separate rule")
            
            # Check for specific rule name patterns
            for name in list(unique_names)[:3]:
                count = rule_names.count(name)
                print(f"   '{name}': {count} rules")
        else:
            print(f"\n✅ Rule names are unique")
            print(f"   But we still have too many rules total")
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 DEBUGGING INCREMENTAL PARSING ISSUE")
    print("=" * 70)
    
    # Test the parsing function directly
    direct_success = test_incremental_parsing_directly()
    
    # Debug why it's not working with uploaded files
    debug_why_not_working()
    
    print(f"\n💡 DIAGNOSIS:")
    if direct_success:
        print(f"   ✅ Incremental parsing function works correctly")
        print(f"   🚨 Issue is with file format or upload processing")
        print(f"   💡 The uploaded file might have a different format")
        print(f"   💡 Or the parsing logic is not being called correctly")
    else:
        print(f"   ❌ Incremental parsing function is broken")
        print(f"   🔧 Need to fix the parse_incremental_set_rule function")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"   1. Check if the uploaded file has the expected format")
    print(f"   2. Verify the incremental parsing function is being called")
    print(f"   3. Debug the rule consolidation logic")
    print(f"   4. Ensure rules with same name are merged correctly")
