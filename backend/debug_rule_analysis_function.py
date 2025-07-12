#!/usr/bin/env python3
"""
Debug the rule analysis function to see why it's not working for SET format and missing shadowed/duplicate rules for XML.
"""

import sqlite3

def debug_rule_analysis_function():
    """Debug the rule analysis function directly."""
    
    print("🔍 DEBUGGING RULE ANALYSIS FUNCTION")
    print("=" * 50)
    
    try:
        # Test with both SET and XML audits
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get a SET format audit
        cursor.execute("""
            SELECT id FROM audit_sessions 
            WHERE filename LIKE '%.txt'
            ORDER BY id DESC 
            LIMIT 1
        """)
        set_audit = cursor.fetchone()
        
        # Get an XML format audit
        cursor.execute("""
            SELECT id FROM audit_sessions 
            WHERE filename LIKE '%.xml'
            ORDER BY id DESC 
            LIMIT 1
        """)
        xml_audit = cursor.fetchone()
        
        conn.close()
        
        if set_audit:
            print(f"\n🔧 Testing SET Format Rule Analysis (Audit {set_audit[0]}):")
            test_rule_analysis_function(set_audit[0], "SET")
        
        if xml_audit:
            print(f"\n📄 Testing XML Format Rule Analysis (Audit {xml_audit[0]}):")
            test_rule_analysis_function(xml_audit[0], "XML")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return False

def test_rule_analysis_function(audit_id, format_type):
    """Test the rule analysis function directly."""
    
    try:
        from src.utils.parse_config import analyze_rule_usage
        
        print(f"   🧪 Calling analyze_rule_usage({audit_id})...")
        
        # Call the function directly
        result = analyze_rule_usage(audit_id)
        
        print(f"   📊 {format_type} Rule Analysis Results:")
        print(f"      Unused Rules: {len(result.get('unused_rules', []))}")
        print(f"      Duplicate Rules: {len(result.get('duplicate_rules', []))}")
        print(f"      Shadowed Rules: {len(result.get('shadowed_rules', []))}")
        print(f"      Overlapping Rules: {len(result.get('overlapping_rules', []))}")
        
        # Show sample results
        for category, items in result.items():
            if items and len(items) > 0:
                print(f"   ✅ {category} ({len(items)} items):")
                for i, item in enumerate(items[:2]):  # Show first 2
                    if isinstance(item, dict):
                        name = item.get('name', item.get('rule_name', 'N/A'))
                        print(f"      {i+1}. {name}")
                    else:
                        print(f"      {i+1}. {str(item)[:50]}...")
            else:
                print(f"   ⚪ {category}: Empty")
        
        # Check if the function is working at all
        total_results = sum(len(items) for items in result.values() if items)
        
        if total_results == 0:
            print(f"   🚨 {format_type} RULE ANALYSIS COMPLETELY BROKEN!")
            print(f"      Function returns empty results for all categories")
            
            # Debug further - check what rules exist
            debug_rules_in_database(audit_id, format_type)
        else:
            print(f"   ✅ {format_type} Rule analysis partially working ({total_results} total results)")
        
        return result
        
    except Exception as e:
        print(f"   ❌ {format_type} Rule analysis function failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def debug_rules_in_database(audit_id, format_type):
    """Debug what rules exist in the database for this audit."""
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
        """, (audit_id,))
        
        rules = cursor.fetchall()
        
        print(f"   🔍 {format_type} Rules in Database ({len(rules)}):")
        for i, rule in enumerate(rules[:5]):  # Show first 5
            rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled = rule
            status = "DISABLED" if is_disabled else "ENABLED"
            print(f"      {i+1}. '{rule_name}' | {src_zone}→{dst_zone} | {src}→{dst} | {service} | {action} | {status}")
        
        if len(rules) > 5:
            print(f"      ... and {len(rules) - 5} more rules")
        
        # Check for obvious duplicates
        rule_signatures = {}
        duplicates_found = 0
        
        for rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled in rules:
            if not is_disabled:
                signature = f"{src_zone}-{dst_zone}-{src}-{dst}-{service}-{action}"
                if signature in rule_signatures:
                    duplicates_found += 1
                    print(f"      🔄 DUPLICATE: '{rule_name}' has same signature as '{rule_signatures[signature]}'")
                else:
                    rule_signatures[signature] = rule_name
        
        disabled_count = sum(1 for rule in rules if rule[7])
        
        print(f"   📊 {format_type} Rule Statistics:")
        print(f"      Total rules: {len(rules)}")
        print(f"      Disabled rules: {disabled_count}")
        print(f"      Manual duplicate detection: {duplicates_found}")
        
        if duplicates_found > 0 and format_type == "XML":
            print(f"      🚨 XML should detect {duplicates_found} duplicates but finds 0!")
        
        if disabled_count > 0:
            print(f"      🚨 Should detect {disabled_count} unused rules but may find 0!")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database debug failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 DEBUGGING RULE ANALYSIS FUNCTION")
    print("=" * 60)
    
    success = debug_rule_analysis_function()
    
    if success:
        print(f"\n💡 DIAGNOSIS:")
        print(f"   Rule analysis function may be failing silently")
        print(f"   Different behavior for SET vs XML formats")
        print(f"   Need to fix the analyze_rule_usage function")
    else:
        print(f"\n❌ Could not debug rule analysis function")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"   1. Fix analyze_rule_usage function")
    print(f"   2. Ensure it works for both SET and XML formats")
    print(f"   3. Fix duplicate and shadowed rule detection")
    print(f"   4. Test with both format types")
