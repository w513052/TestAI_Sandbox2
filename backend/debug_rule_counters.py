#!/usr/bin/env python3
"""
Debug the rule counters to understand why they're overinflated.
"""

import requests
import sqlite3

def debug_rule_counters():
    """Debug the rule counter inflation issue."""
    
    print("🔍 DEBUGGING RULE COUNTER INFLATION")
    print("=" * 50)
    
    try:
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
        print(f"📋 Debugging Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        # Get all rules from database
        cursor.execute("""
            SELECT rule_name, rule_type, src, dst, service, action, position, is_disabled
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
        """, (audit_id,))
        
        rules = cursor.fetchall()
        print(f"\n📊 Database Rules Analysis:")
        print(f"   Total rules in database: {len(rules)}")
        
        # Categorize rules
        enabled_rules = [r for r in rules if not r[7]]
        disabled_rules = [r for r in rules if r[7]]
        
        print(f"   Enabled rules: {len(enabled_rules)}")
        print(f"   Disabled rules: {len(disabled_rules)}")
        
        # Show sample rules
        print(f"\n📋 Sample Rules:")
        for i, rule in enumerate(rules[:10]):
            rule_name, rule_type, src, dst, service, action, position, is_disabled = rule
            status = "DISABLED" if is_disabled else "ENABLED"
            print(f"   {i+1}. {rule_name} | {src} → {dst} | {service} | {action} | Pos:{position} ({status})")
        
        conn.close()
        
        # Get API analysis results
        print(f"\n🌐 API Analysis Results:")
        analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()['data']
            summary = analysis_data['analysis_summary']
            
            print(f"📈 Analysis Summary:")
            print(f"   total_rules: {summary['total_rules']}")
            print(f"   disabled_rules_count: {summary.get('disabled_rules_count', 0)}")
            
            # Check each rule analysis category
            categories = {
                'unusedRules': 'Unused Rules',
                'duplicateRules': 'Duplicate Rules',
                'shadowedRules': 'Shadowed Rules',
                'overlappingRules': 'Overlapping Rules'
            }
            
            print(f"\n📋 Rule Analysis Categories:")
            total_issues = 0
            for key, name in categories.items():
                items = analysis_data.get(key, [])
                print(f"   {name}: {len(items)} items")
                total_issues += len(items)
                
                # Show sample items for detailed analysis
                if len(items) > 0:
                    print(f"      Sample items:")
                    for i, item in enumerate(items[:3]):
                        if key == 'duplicateRules':
                            orig = item.get('original_rule', {}).get('name', 'N/A')
                            dup = item.get('duplicate_rule', {}).get('name', 'N/A')
                            print(f"      {i+1}. {dup} duplicates {orig}")
                        elif key == 'shadowedRules':
                            shadowed = item.get('name', 'N/A')
                            shadower = item.get('shadowed_by', {}).get('name', 'N/A')
                            print(f"      {i+1}. {shadowed} shadowed by {shadower}")
                        elif key == 'overlappingRules':
                            rule1 = item.get('rule1', {}).get('name', 'N/A')
                            rule2 = item.get('rule2', {}).get('name', 'N/A')
                            print(f"      {i+1}. {rule1} overlaps {rule2}")
                        else:
                            print(f"      {i+1}. {item.get('name', 'N/A')} - {item.get('description', 'N/A')}")
            
            print(f"\n🔍 Rule Counter Analysis:")
            print(f"   Database rules: {len(rules)}")
            print(f"   API total_rules: {summary['total_rules']}")
            print(f"   Total rule issues found: {total_issues}")
            
            # Check for double counting
            print(f"\n🚨 Potential Issues:")
            
            if summary['total_rules'] != len(rules):
                print(f"   ❌ Mismatch: API total_rules ({summary['total_rules']}) != Database rules ({len(rules)})")
            else:
                print(f"   ✅ Total rule count matches database")
            
            # Check if rule issues are being double-counted
            unused_count = len(analysis_data.get('unusedRules', []))
            duplicate_count = len(analysis_data.get('duplicateRules', []))
            shadowed_count = len(analysis_data.get('shadowedRules', []))
            overlapping_count = len(analysis_data.get('overlappingRules', []))
            
            print(f"\n📊 Rule Issue Breakdown:")
            print(f"   Unused rules: {unused_count}")
            print(f"   Duplicate rules: {duplicate_count}")
            print(f"   Shadowed rules: {shadowed_count}")
            print(f"   Overlapping rules: {overlapping_count}")
            
            # Check for overlaps between categories
            print(f"\n🔍 Checking for Category Overlaps:")
            
            # Get rule names from each category
            unused_names = {item.get('name', '') for item in analysis_data.get('unusedRules', [])}
            duplicate_names = {item.get('duplicate_rule', {}).get('name', '') for item in analysis_data.get('duplicateRules', [])}
            shadowed_names = {item.get('name', '') for item in analysis_data.get('shadowedRules', [])}
            
            # Check overlaps
            unused_duplicate_overlap = unused_names.intersection(duplicate_names)
            unused_shadowed_overlap = unused_names.intersection(shadowed_names)
            duplicate_shadowed_overlap = duplicate_names.intersection(shadowed_names)
            
            if unused_duplicate_overlap:
                print(f"   ⚠️  Unused-Duplicate overlap: {len(unused_duplicate_overlap)} rules")
                print(f"      Rules: {list(unused_duplicate_overlap)[:3]}")
            
            if unused_shadowed_overlap:
                print(f"   ⚠️  Unused-Shadowed overlap: {len(unused_shadowed_overlap)} rules")
                print(f"      Rules: {list(unused_shadowed_overlap)[:3]}")
            
            if duplicate_shadowed_overlap:
                print(f"   ⚠️  Duplicate-Shadowed overlap: {len(duplicate_shadowed_overlap)} rules")
                print(f"      Rules: {list(duplicate_shadowed_overlap)[:3]}")
            
            if not (unused_duplicate_overlap or unused_shadowed_overlap or duplicate_shadowed_overlap):
                print(f"   ✅ No overlaps found between categories")
            
            # Check expected vs actual
            print(f"\n🎯 Expected vs Actual Analysis:")
            
            # Based on your expected breakdown:
            # Total Security Policies: 17 (10 original + 5 redundant + 2 duplicate)
            expected = {
                "total_rules": 17,
                "original_rules": 10,
                "redundant_rules": 5,
                "duplicate_rules": 2,  # You expected 2, but we're finding 7
                "unused_rules": 5,     # Estimate based on redundant rules
            }
            
            actual = {
                "total_rules": summary['total_rules'],
                "duplicate_rules": duplicate_count,
                "unused_rules": unused_count,
                "shadowed_rules": shadowed_count,
                "overlapping_rules": overlapping_count
            }
            
            print(f"   Your expected breakdown:")
            print(f"      Total rules: 17 (10 original + 5 redundant + 2 duplicate)")
            print(f"      Expected duplicates: 2")
            print(f"      Expected redundant: 5")
            
            print(f"   Our analysis results:")
            print(f"      Total rules: {actual['total_rules']}")
            print(f"      Duplicate rules: {actual['duplicate_rules']} {'❌ OVERINFLATED' if actual['duplicate_rules'] > 2 else '✅'}")
            print(f"      Unused rules: {actual['unused_rules']} {'❌ OVERINFLATED' if actual['unused_rules'] > 5 else '✅'}")
            print(f"      Shadowed rules: {actual['shadowed_rules']} {'❌ OVERINFLATED' if actual['shadowed_rules'] > 5 else '✅'}")
            
            # Identify the inflation issue
            if actual['duplicate_rules'] > expected['duplicate_rules']:
                inflation = actual['duplicate_rules'] - expected['duplicate_rules']
                print(f"\n🚨 DUPLICATE RULES OVERINFLATED by {inflation}")
                print(f"   Expected: 2 duplicate rules")
                print(f"   Found: {actual['duplicate_rules']} duplicate rules")
                print(f"   Issue: Rule analysis logic may be too aggressive")
            
            return audit_id
            
        else:
            print(f"❌ Analysis request failed: {analysis_response.status_code}")
            return None
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def suggest_rule_counter_fixes():
    """Suggest fixes for rule counter inflation."""
    
    print(f"\n🔧 RULE COUNTER FIXES NEEDED:")
    print("=" * 40)
    
    print(f"1. **Duplicate Rule Detection Too Aggressive:**")
    print(f"   - Current logic may be finding too many duplicates")
    print(f"   - Need stricter criteria for what constitutes a duplicate")
    print(f"   - Consider only exact matches, not similar rules")
    
    print(f"\n2. **Rule Analysis Logic Review:**")
    print(f"   - Review rule signature creation in rule_analysis.py")
    print(f"   - Ensure disabled rules aren't double-counted")
    print(f"   - Check if redundant rules are being marked as duplicates")
    
    print(f"\n3. **Category Overlap Issues:**")
    print(f"   - Rules might be appearing in multiple categories")
    print(f"   - Need to prioritize categories (e.g., disabled > duplicate)")
    print(f"   - Avoid counting the same rule multiple times")

if __name__ == "__main__":
    print("🚀 DEBUGGING RULE COUNTER INFLATION")
    print("=" * 60)
    
    audit_id = debug_rule_counters()
    
    if audit_id:
        suggest_rule_counter_fixes()
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Review rule analysis logic for over-aggressive detection")
        print(f"   2. Implement stricter duplicate rule criteria")
        print(f"   3. Ensure no double-counting between categories")
        print(f"   4. Test with expected breakdown: 2 duplicates, not 7+")
    else:
        print(f"\n❌ Could not debug - no recent audit found")
