#!/usr/bin/env python3
"""
Debug set format object usage analysis to understand why objects aren't being matched.
"""

import sqlite3

def debug_set_object_usage():
    """Debug the set format object usage issue."""
    
    print("🔍 DEBUGGING SET FORMAT OBJECT USAGE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get the most recent audit (should be the set format test)
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
        print(f"📋 Debugging Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        # Get rules and their object references
        cursor.execute("""
            SELECT rule_name, src, dst, service, raw_xml
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
            LIMIT 10
        """, (audit_id,))
        
        rules = cursor.fetchall()
        print(f"\n📊 Rules and Object References:")
        print(f"   Total rules: {len(rules)}")
        
        for i, rule in enumerate(rules[:5]):
            rule_name, src, dst, service, raw_xml = rule
            print(f"   {i+1}. {rule_name}:")
            print(f"      Source: '{src}'")
            print(f"      Destination: '{dst}'")
            print(f"      Service: '{service}'")
            print(f"      Raw: {raw_xml[:80]}...")
        
        # Get objects and their names
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_id = ?
            ORDER BY object_type, name
        """, (audit_id,))
        
        objects = cursor.fetchall()
        print(f"\n📦 Objects and Usage:")
        print(f"   Total objects: {len(objects)}")
        
        address_objects = [obj for obj in objects if obj[1] == 'address']
        service_objects = [obj for obj in objects if obj[1] == 'service']
        
        print(f"   Address objects ({len(address_objects)}):")
        for obj in address_objects[:10]:
            name, obj_type, value, used_count = obj
            print(f"      '{name}' = {value} | Used: {used_count}")
        
        print(f"   Service objects ({len(service_objects)}):")
        for obj in service_objects:
            name, obj_type, value, used_count = obj
            print(f"      '{name}' = {value} | Used: {used_count}")
        
        # Manual object usage check
        print(f"\n🔍 Manual Object Usage Check:")
        
        # Check if object names match rule references
        object_names = {obj[0] for obj in objects}
        rule_references = set()
        
        for rule in rules:
            rule_name, src, dst, service, raw_xml = rule
            if src and src != 'any':
                rule_references.add(src)
            if dst and dst != 'any':
                rule_references.add(dst)
            if service and service != 'any' and not service.startswith('service-'):
                rule_references.add(service)
        
        print(f"   Object names in database: {sorted(list(object_names))[:10]}...")
        print(f"   Object references in rules: {sorted(list(rule_references))}")
        
        # Check for quote issues
        quoted_references = {ref.strip('"\'') for ref in rule_references}
        quoted_objects = {name.strip('"\'') for name in object_names}
        
        print(f"\n🔧 Quote Analysis:")
        print(f"   Rule references (unquoted): {sorted(list(quoted_references))}")
        print(f"   Object names (unquoted): {sorted(list(quoted_objects))[:10]}...")
        
        # Find matches
        matches = quoted_references.intersection(quoted_objects)
        print(f"   Matches found: {sorted(list(matches))}")
        
        if not matches:
            print(f"   ❌ No matches found - this explains why all objects are unused!")
            print(f"   🔧 The issue is likely in quote handling during parsing or analysis")
        else:
            print(f"   ✅ {len(matches)} matches found")
        
        conn.close()
        
        return audit_id
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def suggest_set_format_fixes():
    """Suggest fixes for set format object usage issues."""
    
    print(f"\n🔧 SET FORMAT FIXES NEEDED:")
    print("=" * 40)
    
    print(f"1. **Quote Handling in Rule Parsing:**")
    print(f"   - Set format rules use quoted object names: \"Client-LAN-01\"")
    print(f"   - Rule parsing might be storing quotes in the field values")
    print(f"   - Object usage analysis needs to handle quoted references")
    
    print(f"\n2. **Object Reference Normalization:**")
    print(f"   - Strip quotes from rule field values during parsing")
    print(f"   - Or strip quotes during object usage analysis")
    print(f"   - Ensure consistent naming between objects and rule references")
    
    print(f"\n3. **Set Format Specific Analysis:**")
    print(f"   - Set format might need different object usage logic")
    print(f"   - Consider case sensitivity issues")
    print(f"   - Handle built-in services (service-http, service-https)")

if __name__ == "__main__":
    audit_id = debug_set_object_usage()
    
    if audit_id:
        suggest_set_format_fixes()
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Fix quote handling in set format rule parsing")
        print(f"   2. Update object usage analysis for set format")
        print(f"   3. Test with the set format file again")
        print(f"   4. Verify object usage counts are correct")
    else:
        print(f"\n❌ Could not debug - no set format audit found")
