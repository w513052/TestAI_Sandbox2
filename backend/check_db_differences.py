#!/usr/bin/env python3
"""
Check database differences between SET and CSV uploads.
"""

import sqlite3

def check_recent_uploads():
    """Check the most recent uploads and their differences."""
    
    print("🔍 CHECKING DATABASE DIFFERENCES: SET vs CSV")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get recent audits
        cursor.execute('''
            SELECT id, session_name, filename 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 5
        ''')
        
        audits = cursor.fetchall()
        print("📋 Recent Audits:")
        for audit_id, session_name, filename in audits:
            format_type = "SET" if ".txt" in filename else "CSV" if ".csv" in filename else "XML" if ".xml" in filename else "UNKNOWN"
            print(f"   {audit_id}: {filename} ({format_type})")
        
        if len(audits) >= 2:
            # Compare the last two audits
            audit1 = audits[0]  # Most recent
            audit2 = audits[1]  # Second most recent
            
            format1 = "SET" if ".txt" in audit1[2] else "CSV" if ".csv" in audit1[2] else "UNKNOWN"
            format2 = "SET" if ".txt" in audit2[2] else "CSV" if ".csv" in audit2[2] else "UNKNOWN"
            
            print(f"\n🔄 Comparing:")
            print(f"   {format1}: Audit {audit1[0]} - {audit1[2]}")
            print(f"   {format2}: Audit {audit2[0]} - {audit2[2]}")
            
            # Compare database contents
            compare_database_data(cursor, audit1[0], format1, audit2[0], format2)
            
            # Check for parsing differences
            check_parsing_differences(cursor, audit1[0], format1, audit2[0], format2)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def compare_database_data(cursor, audit1_id, format1, audit2_id, format2):
    """Compare the actual data stored in the database."""
    
    print(f"\n📊 Database Content Comparison:")
    
    results = {}
    
    for audit_id, format_name in [(audit1_id, format1), (audit2_id, format2)]:
        # Count objects and rules
        cursor.execute('SELECT COUNT(*) FROM object_definitions WHERE audit_id = ?', (audit_id,))
        obj_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ?', (audit_id,))
        rule_count = cursor.fetchone()[0]
        
        results[format_name] = {'objects': obj_count, 'rules': rule_count}
        
        print(f"   {format_name}: {obj_count} objects, {rule_count} rules")
        
        # Get object details
        cursor.execute('''
            SELECT name, object_type, value, used_in_rules 
            FROM object_definitions 
            WHERE audit_id = ? 
            ORDER BY name
        ''', (audit_id,))
        
        objects = cursor.fetchall()
        print(f"      Objects:")
        for name, obj_type, value, used_in_rules in objects[:8]:  # Show first 8
            print(f"         {name} ({obj_type}) = '{value}' | Used: {used_in_rules}")
        if len(objects) > 8:
            print(f"         ... and {len(objects) - 8} more objects")
        
        # Get rule details
        cursor.execute('''
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action, position 
            FROM firewall_rules 
            WHERE audit_id = ? 
            ORDER BY position
        ''', (audit_id,))
        
        rules = cursor.fetchall()
        print(f"      Rules:")
        for rule_name, src_zone, dst_zone, src, dst, service, action, position in rules[:5]:  # Show first 5
            print(f"         {position}. {rule_name}: {src_zone}→{dst_zone} | {src}→{dst} | {service} | {action}")
        if len(rules) > 5:
            print(f"         ... and {len(rules) - 5} more rules")
    
    # Compare counts
    if len(results) == 2:
        formats = list(results.keys())
        format1, format2 = formats[0], formats[1]
        
        print(f"\n📈 Count Comparison:")
        obj_diff = results[format1]['objects'] - results[format2]['objects']
        rule_diff = results[format1]['rules'] - results[format2]['rules']
        
        print(f"   Object difference: {obj_diff} ({format1}: {results[format1]['objects']}, {format2}: {results[format2]['objects']})")
        print(f"   Rule difference: {rule_diff} ({format1}: {results[format1]['rules']}, {format2}: {results[format2]['rules']})")
        
        if obj_diff != 0 or rule_diff != 0:
            print(f"   🚨 DIFFERENCE DETECTED! Same config producing different counts")
        else:
            print(f"   ✅ Same counts - difference likely in analysis logic")

def check_parsing_differences(cursor, audit1_id, format1, audit2_id, format2):
    """Check for specific parsing differences."""
    
    print(f"\n🔍 Parsing Difference Analysis:")
    
    # Check for objects with same names but different values
    cursor.execute('''
        SELECT o1.name, o1.value as value1, o2.value as value2
        FROM object_definitions o1
        JOIN object_definitions o2 ON o1.name = o2.name
        WHERE o1.audit_id = ? AND o2.audit_id = ? AND o1.value != o2.value
    ''', (audit1_id, audit2_id))
    
    value_diffs = cursor.fetchall()
    if value_diffs:
        print(f"   🔄 Objects with different values:")
        for name, value1, value2 in value_diffs:
            print(f"      {name}: '{value1}' vs '{value2}'")
    else:
        print(f"   ✅ No objects with different values found")
    
    # Check for rules with same names but different properties
    cursor.execute('''
        SELECT r1.rule_name, r1.src, r1.dst, r1.service, r2.src, r2.dst, r2.service
        FROM firewall_rules r1
        JOIN firewall_rules r2 ON r1.rule_name = r2.rule_name
        WHERE r1.audit_id = ? AND r2.audit_id = ? 
        AND (r1.src != r2.src OR r1.dst != r2.dst OR r1.service != r2.service)
    ''', (audit1_id, audit2_id))
    
    rule_diffs = cursor.fetchall()
    if rule_diffs:
        print(f"   🔄 Rules with different properties:")
        for rule_name, src1, dst1, svc1, src2, dst2, svc2 in rule_diffs:
            print(f"      {rule_name}:")
            print(f"         {format1}: {src1}→{dst1} | {svc1}")
            print(f"         {format2}: {src2}→{dst2} | {svc2}")
    else:
        print(f"   ✅ No rules with different properties found")

def suggest_investigation_steps():
    """Suggest next steps for investigation."""
    
    print(f"\n💡 Investigation Steps:")
    print(f"   1. **Check Parser Logic:**")
    print(f"      - Compare SET parser vs CSV parser in parse_config.py")
    print(f"      - Look for format-specific field extraction")
    
    print(f"   2. **Check Analysis Pipeline:**")
    print(f"      - Verify analysis logic handles both formats consistently")
    print(f"      - Check rule signature generation")
    print(f"      - Check object usage calculation")
    
    print(f"   3. **Test with Simple Config:**")
    print(f"      - Create identical simple config in both formats")
    print(f"      - Compare parsing results step by step")

if __name__ == "__main__":
    print("🚀 INVESTIGATING SET vs CSV PARSING DIFFERENCES")
    print("=" * 60)
    
    check_recent_uploads()
    suggest_investigation_steps()
    
    print(f"\n🎯 Key Question: Are the differences in:")
    print(f"   A) Parsing (different data extracted from same config)")
    print(f"   B) Analysis (same data analyzed differently)")
    print(f"   C) Both parsing and analysis")
