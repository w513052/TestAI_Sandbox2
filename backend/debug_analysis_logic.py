#!/usr/bin/env python3
"""
Debug why the analysis logic is not detecting obvious duplicates and unused items.
"""

import sqlite3

def debug_analysis_logic():
    """Debug the analysis logic to see why it's missing obvious issues."""
    
    print("🔍 DEBUGGING ANALYSIS LOGIC")
    print("=" * 50)
    
    try:
        # Get the most recent audit
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM audit_sessions ORDER BY id DESC LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ No audit sessions found")
            return
        
        audit_id = audit[0]
        
        # Get all objects
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_id = ?
            ORDER BY name
        """, (audit_id,))
        
        objects = cursor.fetchall()
        
        print(f"📦 Objects in Database ({len(objects)}):")
        for i, obj in enumerate(objects):
            name, obj_type, value, used_in_rules = obj
            print(f"   {i+1}. '{name}' ({obj_type}) = {value} | Used: {used_in_rules}")
        
        # Get all rules
        cursor.execute("""
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY rule_name
        """, (audit_id,))
        
        rules = cursor.fetchall()
        
        print(f"\n📋 Rules in Database ({len(rules)}):")
        for i, rule in enumerate(rules):
            rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled = rule
            status = "DISABLED" if is_disabled else "ENABLED"
            print(f"   {i+1}. '{rule_name}' | {src_zone}→{dst_zone} | {src}→{dst} | {service} | {action} | {status}")
        
        # Manual duplicate detection
        print(f"\n🔍 Manual Duplicate Detection:")
        
        # Check for duplicate objects (same value)
        object_values = {}
        duplicate_objects = []
        
        for name, obj_type, value, used_in_rules in objects:
            key = f"{obj_type}:{value}"
            if key in object_values:
                original = object_values[key]
                duplicate_objects.append((name, original, value))
                print(f"   DUPLICATE OBJECT: '{name}' duplicates '{original}' (both = {value})")
            else:
                object_values[key] = name
        
        print(f"   Manual duplicate objects found: {len(duplicate_objects)}")
        
        # Check for duplicate rules (same signature)
        rule_signatures = {}
        duplicate_rules = []
        
        for rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled in rules:
            if not is_disabled:  # Only check enabled rules
                signature = f"{src_zone}-{dst_zone}-{src}-{dst}-{service}-{action}"
                if signature in rule_signatures:
                    original = rule_signatures[signature]
                    duplicate_rules.append((rule_name, original))
                    print(f"   DUPLICATE RULE: '{rule_name}' duplicates '{original}'")
                else:
                    rule_signatures[signature] = rule_name
        
        print(f"   Manual duplicate rules found: {len(duplicate_rules)}")
        
        # Check for unused objects (used_in_rules = 0)
        unused_objects = [name for name, obj_type, value, used_in_rules in objects if used_in_rules == 0]
        print(f"\n📦 Manual Unused Objects: {len(unused_objects)}")
        for name in unused_objects:
            print(f"   - {name}")
        
        # Check for unused rules (disabled or not referenced)
        unused_rules = [rule_name for rule_name, src_zone, dst_zone, src, dst, service, action, is_disabled in rules if is_disabled]
        print(f"\n📋 Manual Unused Rules: {len(unused_rules)}")
        for name in unused_rules:
            print(f"   - {name}")
        
        # Summary of manual analysis
        print(f"\n📊 Manual Analysis Summary:")
        print(f"   Total objects: {len(objects)}")
        print(f"   Total rules: {len(rules)}")
        print(f"   Duplicate objects: {len(duplicate_objects)}")
        print(f"   Duplicate rules: {len(duplicate_rules)}")
        print(f"   Unused objects: {len(unused_objects)}")
        print(f"   Unused rules: {len(unused_rules)}")
        
        # Compare with expected
        expected = {
            "duplicate_objects": 2,
            "duplicate_rules": 2,
            "unused_objects": 1,
            "unused_rules": 1
        }
        
        actual = {
            "duplicate_objects": len(duplicate_objects),
            "duplicate_rules": len(duplicate_rules),
            "unused_objects": len(unused_objects),
            "unused_rules": len(unused_rules)
        }
        
        print(f"\n🎯 Manual Analysis vs Expected:")
        for key in expected:
            expected_val = expected[key]
            actual_val = actual[key]
            status = "✅" if actual_val == expected_val else "❌"
            print(f"   {key}: Expected={expected_val}, Manual={actual_val} {status}")
        
        conn.close()
        
        return actual
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def identify_analysis_issues(manual_results):
    """Identify what's wrong with the analysis logic."""
    
    if not manual_results:
        return
    
    print(f"\n🔧 ANALYSIS ISSUES IDENTIFIED:")
    print("=" * 40)
    
    if manual_results['duplicate_objects'] > 0:
        print(f"1. **Duplicate Object Detection Broken:**")
        print(f"   - Manual analysis finds {manual_results['duplicate_objects']} duplicate objects")
        print(f"   - System analysis finds 0 duplicate objects")
        print(f"   - Fix: Check redundant object detection logic")
    
    if manual_results['duplicate_rules'] > 0:
        print(f"\n2. **Duplicate Rule Detection Broken:**")
        print(f"   - Manual analysis finds {manual_results['duplicate_rules']} duplicate rules")
        print(f"   - System analysis finds 0 duplicate rules")
        print(f"   - Fix: Check duplicate rule detection logic")
    
    if manual_results['unused_objects'] > 0:
        print(f"\n3. **Unused Object Detection Broken:**")
        print(f"   - Manual analysis finds {manual_results['unused_objects']} unused objects")
        print(f"   - System analysis finds 0 unused objects")
        print(f"   - Fix: Check object usage analysis logic")
    
    if manual_results['unused_rules'] > 0:
        print(f"\n4. **Unused Rule Detection Broken:**")
        print(f"   - Manual analysis finds {manual_results['unused_rules']} unused rules")
        print(f"   - System analysis finds 0 unused rules")
        print(f"   - Fix: Check unused rule detection logic")
    
    print(f"\n🚨 ROOT CAUSE:")
    print(f"   The analysis logic is too lenient/broken")
    print(f"   It's not detecting obvious duplicates and unused items")
    print(f"   This is the opposite of the previous over-aggressive problem")

if __name__ == "__main__":
    print("🚀 DEBUGGING ANALYSIS LOGIC")
    print("=" * 60)
    
    manual_results = debug_analysis_logic()
    
    if manual_results:
        identify_analysis_issues(manual_results)
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Fix duplicate object detection logic")
        print(f"   2. Fix duplicate rule detection logic")
        print(f"   3. Fix unused object detection logic")
        print(f"   4. Fix unused rule detection logic")
        print(f"   5. Test with your simple 8-object, 8-rule breakdown")
    else:
        print(f"\n❌ Could not debug analysis logic")
