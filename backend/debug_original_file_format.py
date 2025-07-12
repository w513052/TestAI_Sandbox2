#!/usr/bin/env python3
"""
Debug the original file format to understand why it's creating 119 rules.
"""

import sqlite3

def debug_original_file_format():
    """Debug the original file format."""
    
    print("🔍 DEBUGGING ORIGINAL FILE FORMAT")
    print("=" * 50)
    
    try:
        # Get the audit with the original file
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Look for the original complex file
        cursor.execute("""
            SELECT id, session_name, filename 
            FROM audit_sessions 
            WHERE filename LIKE '%sample3%' OR session_name LIKE '%sample3%'
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ Original file audit not found")
            return
        
        audit_id, session_name, filename = audit
        print(f"📋 Original File Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        # Get sample rules to understand the pattern
        cursor.execute("""
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action, raw_xml
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
            LIMIT 20
        """, (audit_id,))
        
        rules = cursor.fetchall()
        
        print(f"\n📋 Sample Rules from Original File:")
        print(f"   Total rules in database: {len(rules)} (showing first 20)")
        
        for i, rule in enumerate(rules):
            rule_name, src_zone, dst_zone, src, dst, service, action, raw_xml = rule
            print(f"\n   {i+1:2d}. Rule Name: '{rule_name}'")
            print(f"       Zones: {src_zone} → {dst_zone}")
            print(f"       Objects: {src} → {dst}")
            print(f"       Service: {service}")
            print(f"       Action: {action}")
            print(f"       Raw: {raw_xml[:150]}...")
        
        # Analyze the raw_xml patterns
        print(f"\n🔍 Raw Command Analysis:")
        raw_commands = [rule[7] for rule in rules[:10]]
        
        for i, raw in enumerate(raw_commands):
            print(f"   {i+1}. {raw}")
        
        # Check if these are individual set commands or complete rules
        print(f"\n📊 Pattern Analysis:")
        
        # Count how many rules have the same base name
        rule_names = [rule[0] for rule in rules]
        from collections import Counter
        name_counts = Counter(rule_names)
        
        print(f"   Rule name frequency:")
        for name, count in list(name_counts.items())[:10]:
            print(f"      '{name}': {count} occurrences")
        
        # Check if rule names contain attribute descriptions
        attribute_patterns = ['from ', 'to ', 'source ', 'destination ', 'service ', 'action ']
        rules_with_attributes = []
        
        for rule_name in rule_names[:20]:
            for pattern in attribute_patterns:
                if pattern in rule_name.lower():
                    rules_with_attributes.append((rule_name, pattern))
                    break
        
        print(f"\n🚨 Rules with attribute patterns in name:")
        for rule_name, pattern in rules_with_attributes[:10]:
            print(f"      '{rule_name}' contains '{pattern.strip()}'")
        
        # Determine the actual file format
        print(f"\n💡 FILE FORMAT DIAGNOSIS:")
        
        if len(rules_with_attributes) > 10:
            print(f"   🚨 ISSUE IDENTIFIED: Rule names contain attribute descriptions!")
            print(f"   📋 Pattern: Each set command attribute is being parsed as a separate rule")
            print(f"   💡 Example: 'Allow-Web-Access from trust' should be part of 'Allow-Web-Access'")
            print(f"   🔧 Fix needed: Parser is not consolidating incremental set commands")
            
            # Show the consolidation that should happen
            print(f"\n🔧 CONSOLIDATION NEEDED:")
            base_names = set()
            for name in rule_names:
                # Extract base rule name (before attribute keywords)
                base_name = name
                for pattern in attribute_patterns:
                    if pattern.strip() in name.lower():
                        base_name = name.split(pattern.strip())[0].strip()
                        break
                base_names.add(base_name)
            
            print(f"   Current rules: {len(rules)} individual set commands")
            print(f"   Should be: {len(base_names)} consolidated rules")
            print(f"   Base rule names: {list(base_names)[:10]}")
            
            return {
                'format_type': 'incremental_with_names',
                'total_rules': len(rules),
                'should_be_rules': len(base_names),
                'base_names': list(base_names)
            }
        else:
            print(f"   ✅ Rule names look normal")
            print(f"   🔍 Issue might be elsewhere")
            return {
                'format_type': 'unknown',
                'total_rules': len(rules)
            }
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def suggest_parser_fix(diagnosis):
    """Suggest how to fix the parser based on the diagnosis."""
    
    if not diagnosis:
        return
    
    print(f"\n🔧 PARSER FIX RECOMMENDATIONS:")
    print("=" * 40)
    
    if diagnosis['format_type'] == 'incremental_with_names':
        print(f"1. **Issue**: Rule names include attribute descriptions")
        print(f"   Example: 'Allow-Web-Access from trust' instead of 'Allow-Web-Access'")
        
        print(f"\n2. **Root Cause**: Set format parsing is creating rule names with attributes")
        print(f"   Each 'set security rules \"Name\" attribute value' becomes a separate rule")
        
        print(f"\n3. **Fix Strategy**: Modify incremental parsing to extract clean rule names")
        print(f"   - Extract base rule name (before attribute keywords)")
        print(f"   - Group all attributes under the same base name")
        print(f"   - Consolidate into single rules")
        
        print(f"\n4. **Expected Result**:")
        print(f"   Before: {diagnosis['total_rules']} individual attribute rules")
        print(f"   After: {diagnosis['should_be_rules']} consolidated rules")
        
        print(f"\n5. **Implementation**: Update parse_incremental_set_rule function")
        print(f"   - Clean rule name extraction")
        print(f"   - Better attribute detection")
        print(f"   - Proper rule consolidation")

if __name__ == "__main__":
    print("🚀 DEBUGGING ORIGINAL FILE FORMAT")
    print("=" * 60)
    
    diagnosis = debug_original_file_format()
    
    if diagnosis:
        suggest_parser_fix(diagnosis)
        
        print(f"\n💡 SUMMARY:")
        print(f"   📁 Original file format identified")
        print(f"   🚨 Parser creating too many rules due to naming issue")
        print(f"   🔧 Fix: Update incremental parsing logic")
        print(f"   🎯 Goal: {diagnosis.get('should_be_rules', 17)} rules instead of {diagnosis.get('total_rules', 119)}")
    else:
        print(f"\n❌ Could not diagnose the issue")
        print(f"   Need to investigate further")
