#!/usr/bin/env python3
"""
Debug the rule analysis logic to understand why it's finding too many issues.
"""

import sqlite3

def debug_rule_analysis_logic():
    """Debug why rule analysis is finding too many issues."""
    
    print("🔍 DEBUGGING RULE ANALYSIS LOGIC")
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
        
        # Get all rules
        cursor.execute("""
            SELECT rule_name, rule_type, src_zone, dst_zone, src, dst, service, action, position, is_disabled
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
        """, (audit_id,))
        
        rules = cursor.fetchall()
        print(f"📊 Total Rules in Database: {len(rules)}")
        
        # Analyze the rules manually
        print(f"\n📋 Rule Analysis:")
        
        enabled_rules = []
        disabled_rules = []
        
        for rule in rules:
            rule_name, rule_type, src_zone, dst_zone, src, dst, service, action, position, is_disabled = rule
            
            if is_disabled:
                disabled_rules.append(rule)
            else:
                enabled_rules.append(rule)
            
            print(f"   {position:2d}. {rule_name}")
            print(f"       {src_zone} → {dst_zone} | {src} → {dst} | {service} | {action} | {'DISABLED' if is_disabled else 'ENABLED'}")
        
        print(f"\n📈 Rule Categorization:")
        print(f"   Enabled rules: {len(enabled_rules)}")
        print(f"   Disabled rules: {len(disabled_rules)}")
        
        # Manual duplicate detection
        print(f"\n🔍 Manual Duplicate Analysis:")
        rule_signatures = {}
        actual_duplicates = []
        
        for rule in rules:
            rule_name, rule_type, src_zone, dst_zone, src, dst, service, action, position, is_disabled = rule
            
            # Create a simple signature
            signature = f"{src_zone}-{dst_zone}-{src}-{dst}-{service}-{action}"
            
            if signature in rule_signatures:
                original_rule = rule_signatures[signature]
                actual_duplicates.append((original_rule[0], rule_name))
                print(f"   DUPLICATE: '{rule_name}' duplicates '{original_rule[0]}'")
            else:
                rule_signatures[signature] = rule
        
        print(f"   Actual duplicates found: {len(actual_duplicates)}")
        
        # Manual unused rule analysis
        print(f"\n🔍 Manual Unused Rule Analysis:")
        actual_unused = []
        
        for rule in rules:
            rule_name, rule_type, src_zone, dst_zone, src, dst, service, action, position, is_disabled = rule
            
            # Simple unused criteria
            if is_disabled:
                actual_unused.append(rule_name)
                print(f"   UNUSED: '{rule_name}' (disabled)")
        
        print(f"   Actual unused rules: {len(actual_unused)}")
        
        # Manual shadowed rule analysis
        print(f"\n🔍 Manual Shadowed Rule Analysis:")
        actual_shadowed = []
        
        # Very simple shadowing check - rules with identical signatures where one comes before another
        for i, rule1 in enumerate(rules):
            for j, rule2 in enumerate(rules):
                if i < j:  # rule1 comes before rule2
                    rule1_name, _, src_zone1, dst_zone1, src1, dst1, service1, action1, _, disabled1 = rule1
                    rule2_name, _, src_zone2, dst_zone2, src2, dst2, service2, action2, _, disabled2 = rule2
                    
                    # If rule1 has broader or equal scope and same action, it shadows rule2
                    if (action1 == action2 and not disabled1 and not disabled2 and
                        src_zone1 == src_zone2 and dst_zone1 == dst_zone2 and
                        src1 == src2 and dst1 == dst2 and service1 == service2):
                        actual_shadowed.append(rule2_name)
                        print(f"   SHADOWED: '{rule2_name}' shadowed by '{rule1_name}'")
        
        print(f"   Actual shadowed rules: {len(actual_shadowed)}")
        
        # Summary
        print(f"\n📊 Manual Analysis Summary:")
        print(f"   Total rules: {len(rules)}")
        print(f"   Disabled (unused): {len(disabled_rules)}")
        print(f"   Duplicates: {len(actual_duplicates)}")
        print(f"   Shadowed: {len(actual_shadowed)}")
        print(f"   Overlapping: 0 (need better logic)")
        
        # Expected vs current analysis
        print(f"\n🎯 Expected vs Current Analysis:")
        print(f"   Expected total rules: 17")
        print(f"   Expected duplicates: 2")
        print(f"   Expected unused: 0-2")
        print(f"   Expected shadowed: 0-2")
        print(f"   Expected overlapping: 0-5")
        
        print(f"\n   Current analysis finds:")
        print(f"   Total rules: {len(rules)} {'✅' if len(rules) == 17 else '❌'}")
        print(f"   Duplicates: {len(actual_duplicates)} {'✅' if len(actual_duplicates) <= 2 else '❌'}")
        print(f"   Unused: {len(actual_unused)} {'✅' if len(actual_unused) <= 2 else '❌'}")
        print(f"   Shadowed: {len(actual_shadowed)} {'✅' if len(actual_shadowed) <= 2 else '❌'}")
        
        conn.close()
        
        return {
            'total_rules': len(rules),
            'duplicates': len(actual_duplicates),
            'unused': len(actual_unused),
            'shadowed': len(actual_shadowed)
        }
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 DEBUGGING RULE ANALYSIS LOGIC")
    print("=" * 60)
    
    results = debug_rule_analysis_logic()
    
    if results:
        print(f"\n💡 ANALYSIS ISSUES IDENTIFIED:")
        
        if results['duplicates'] > 2:
            print(f"   🚨 Duplicate detection too aggressive: {results['duplicates']} found, expected ≤2")
            print(f"      Fix: Use stricter duplicate criteria")
        
        if results['unused'] > 2:
            print(f"   🚨 Unused detection too aggressive: {results['unused']} found, expected ≤2")
            print(f"      Fix: Only count truly unused rules (not just disabled)")
        
        if results['shadowed'] > 2:
            print(f"   🚨 Shadowed detection too aggressive: {results['shadowed']} found, expected ≤2")
            print(f"      Fix: Use more realistic shadowing logic")
        
        print(f"\n🔧 FIXES NEEDED:")
        print(f"   1. Make duplicate detection stricter")
        print(f"   2. Reduce unused rule criteria")
        print(f"   3. Improve shadowed rule logic")
        print(f"   4. Limit overlapping rule detection")
        print(f"   5. Ensure realistic analysis results")
    else:
        print(f"\n❌ Could not debug rule analysis")
