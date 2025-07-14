#!/usr/bin/env python3
"""
Compare the differences between SET and CSV format uploads of the same configuration.
"""

import sqlite3
import requests

def compare_recent_uploads():
    """Compare the most recent SET and CSV uploads."""
    
    print("🔍 COMPARING SET vs CSV FORMAT UPLOADS")
    print("=" * 50)
    
    try:
        # Get recent audits
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_name, filename 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 5
        ''')
        
        audits = cursor.fetchall()
        print("📋 Recent Audits:")
        for audit_id, session_name, filename in audits:
            print(f"   {audit_id}: {filename} ({session_name})")
        
        if len(audits) >= 2:
            # Assume the last 2 are SET and CSV of same config
            audit1 = audits[0]  # Most recent
            audit2 = audits[1]  # Second most recent
            
            print(f"\n🔄 Comparing Last Two Uploads:")
            print(f"   Audit 1: {audit1[0]} - {audit1[2]}")
            print(f"   Audit 2: {audit2[0]} - {audit2[2]}")
            
            # Determine which is SET and which is CSV
            format1 = "SET" if ".txt" in audit1[2] else "CSV" if ".csv" in audit1[2] else "UNKNOWN"
            format2 = "SET" if ".txt" in audit2[2] else "CSV" if ".csv" in audit2[2] else "UNKNOWN"
            
            print(f"   Format 1: {format1}")
            print(f"   Format 2: {format2}")
            
            # Compare database contents
            compare_database_contents(cursor, audit1[0], format1, audit2[0], format2)
            
            # Compare API analysis results
            compare_analysis_results(audit1[0], format1, audit2[0], format2)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def compare_database_contents(cursor, audit1_id, format1, audit2_id, format2):
    """Compare the database contents for both audits."""
    
    print(f"\n📊 Database Contents Comparison:")
    
    for audit_id, format_name in [(audit1_id, format1), (audit2_id, format2)]:
        # Count objects
        cursor.execute('SELECT COUNT(*) FROM object_definitions WHERE audit_id = ?', (audit_id,))
        obj_count = cursor.fetchone()[0]
        
        # Count rules
        cursor.execute('SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ?', (audit_id,))
        rule_count = cursor.fetchone()[0]
        
        print(f"   {format_name} (ID {audit_id}): {obj_count} objects, {rule_count} rules")
        
        # Show sample objects
        cursor.execute('''
            SELECT name, object_type, value, used_in_rules 
            FROM object_definitions 
            WHERE audit_id = ? 
            ORDER BY name 
            LIMIT 5
        ''', (audit_id,))
        
        objects = cursor.fetchall()
        print(f"      Sample objects:")
        for name, obj_type, value, used_in_rules in objects:
            print(f"         {name} ({obj_type}) = {value} | Used: {used_in_rules}")
        
        # Show sample rules
        cursor.execute('''
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action 
            FROM firewall_rules 
            WHERE audit_id = ? 
            ORDER BY position 
            LIMIT 3
        ''', (audit_id,))
        
        rules = cursor.fetchall()
        print(f"      Sample rules:")
        for rule_name, src_zone, dst_zone, src, dst, service, action in rules:
            print(f"         {rule_name}: {src_zone}→{dst_zone} | {src}→{dst} | {service} | {action}")

def compare_analysis_results(audit1_id, format1, audit2_id, format2):
    """Compare the analysis results from the API."""
    
    print(f"\n📈 Analysis Results Comparison:")
    
    for audit_id, format_name in [(audit1_id, format1), (audit2_id, format2)]:
        try:
            response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
            
            if response.status_code == 200:
                analysis_data = response.json()['data']
                summary = analysis_data['analysis_summary']
                
                print(f"   {format_name} Analysis (ID {audit_id}):")
                print(f"      Total Objects: {summary.get('total_objects', 'N/A')}")
                print(f"      Used Objects: {summary.get('used_objects_count', 'N/A')}")
                print(f"      Unused Objects: {summary.get('unused_objects_count', 'N/A')}")
                print(f"      Redundant Objects: {summary.get('redundant_objects_count', 'N/A')}")
                print(f"      Total Rules: {summary.get('total_rules', 'N/A')}")
                
                # Detailed analysis counts
                unused_rules = len(analysis_data.get('unusedRules', []))
                duplicate_rules = len(analysis_data.get('duplicateRules', []))
                shadowed_rules = len(analysis_data.get('shadowedRules', []))
                overlapping_rules = len(analysis_data.get('overlappingRules', []))
                
                print(f"      Unused Rules: {unused_rules}")
                print(f"      Duplicate Rules: {duplicate_rules}")
                print(f"      Shadowed Rules: {shadowed_rules}")
                print(f"      Overlapping Rules: {overlapping_rules}")
                
                # Show specific differences
                if format_name == format2:  # Second format, compare with first
                    print(f"\n🔍 Key Differences Found:")
                    # This will be filled in when we run both
            else:
                print(f"   {format_name} Analysis: ❌ Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   {format_name} Analysis: ❌ Error - {str(e)}")

def identify_parsing_differences():
    """Identify potential parsing differences between formats."""
    
    print(f"\n🔧 Potential Causes of Differences:")
    print("   1. **Parsing Logic Differences:**")
    print("      - SET format parser vs CSV format parser")
    print("      - Different field extraction methods")
    print("      - Different object/rule identification logic")
    
    print("   2. **Data Structure Differences:**")
    print("      - Field mapping variations")
    print("      - Value normalization differences")
    print("      - Object reference resolution")
    
    print("   3. **Analysis Pipeline Differences:**")
    print("      - Format-specific analysis logic")
    print("      - Different rule signature generation")
    print("      - Object usage calculation variations")

if __name__ == "__main__":
    print("🚀 INVESTIGATING SET vs CSV FORMAT DIFFERENCES")
    print("=" * 60)
    
    compare_recent_uploads()
    identify_parsing_differences()
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Check parsing logic in parse_config.py")
    print(f"   2. Compare field extraction for both formats")
    print(f"   3. Verify analysis pipeline handles both formats consistently")
    print(f"   4. Test with identical simple configuration")
