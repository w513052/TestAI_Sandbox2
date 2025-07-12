#!/usr/bin/env python3
"""
Deep analysis verification to check the actual parsing and analysis logic.
"""

import sqlite3
import requests
import json

def examine_database_content():
    """Examine what's actually stored in the database for the recent upload."""
    
    print("🔍 Deep Database Analysis")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get the most recent audit session
        cursor.execute("""
            SELECT id, session_name, filename, status, start_time 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        recent_audits = cursor.fetchall()
        print(f"\n📋 Recent Audit Sessions:")
        for audit in recent_audits:
            print(f"   ID {audit[0]}: {audit[1]} - {audit[2]} ({audit[3]})")
        
        # Focus on the most recent audit
        latest_audit_id = recent_audits[0][0]
        print(f"\n🎯 Analyzing Audit ID: {latest_audit_id}")
        
        # Check rules for this audit
        cursor.execute("""
            SELECT rule_name, rule_type, src, dst, service, action, is_disabled, position
            FROM firewall_rules 
            WHERE audit_session_id = ?
            ORDER BY position
        """, (latest_audit_id,))
        
        rules = cursor.fetchall()
        print(f"\n📊 Rules Found: {len(rules)}")
        
        if len(rules) > 0:
            print(f"   Sample rules:")
            for i, rule in enumerate(rules[:5]):
                status = "DISABLED" if rule[6] else "ENABLED"
                print(f"   {i+1}. {rule[0]} | {rule[2]} → {rule[3]} | {rule[4]} | {rule[5]} ({status})")
            if len(rules) > 5:
                print(f"   ... and {len(rules) - 5} more rules")
        else:
            print(f"   ❌ No rules found!")
        
        # Check objects for this audit
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_session_id = ?
            ORDER BY name
        """, (latest_audit_id,))
        
        objects = cursor.fetchall()
        print(f"\n📦 Objects Found: {len(objects)}")
        
        if len(objects) > 0:
            used_objects = [obj for obj in objects if obj[3] > 0]
            unused_objects = [obj for obj in objects if obj[3] == 0]
            
            print(f"   Used objects: {len(used_objects)}")
            print(f"   Unused objects: {len(unused_objects)}")
            
            print(f"\n   📋 All Objects:")
            for i, obj in enumerate(objects):
                usage = f"Used in {obj[3]} rules" if obj[3] > 0 else "UNUSED"
                print(f"   {i+1}. {obj[0]} ({obj[1]}) = {obj[2]} | {usage}")
        else:
            print(f"   ❌ No objects found!")
        
        conn.close()
        
        return latest_audit_id, len(rules), len(objects)
        
    except Exception as e:
        print(f"❌ Database analysis failed: {str(e)}")
        return None, 0, 0

def analyze_object_usage_logic(audit_id):
    """Analyze the object usage detection logic."""
    
    print(f"\n🔬 Object Usage Analysis Logic Check")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get all rules and objects for this audit
        cursor.execute("""
            SELECT rule_name, src, dst, service, raw_xml
            FROM firewall_rules 
            WHERE audit_session_id = ?
        """, (audit_id,))
        rules = cursor.fetchall()
        
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_session_id = ?
        """, (audit_id,))
        objects = cursor.fetchall()
        
        print(f"\n🔍 Manual Usage Analysis:")
        print(f"   Rules to analyze: {len(rules)}")
        print(f"   Objects to check: {len(objects)}")
        
        # Manual check - look for object references in rules
        object_usage_count = {}
        for obj_name, obj_type, obj_value, stored_usage in objects:
            object_usage_count[obj_name] = 0
            
            # Check each rule for references to this object
            for rule_name, src, dst, service, raw_xml in rules:
                # Check if object is referenced in rule fields
                if (obj_name in src or obj_name in dst or obj_name in service or 
                    (raw_xml and obj_name in raw_xml)):
                    object_usage_count[obj_name] += 1
        
        print(f"\n📊 Manual vs Stored Usage Comparison:")
        discrepancies = 0
        for obj_name, obj_type, obj_value, stored_usage in objects:
            manual_usage = object_usage_count[obj_name]
            match = "✅" if manual_usage == stored_usage else "❌"
            if manual_usage != stored_usage:
                discrepancies += 1
            print(f"   {obj_name}: Manual={manual_usage}, Stored={stored_usage} {match}")
        
        if discrepancies > 0:
            print(f"\n🚨 Found {discrepancies} discrepancies in usage analysis!")
        else:
            print(f"\n✅ Usage analysis is consistent")
        
        conn.close()
        return discrepancies == 0
        
    except Exception as e:
        print(f"❌ Usage analysis failed: {str(e)}")
        return False

def check_api_analysis_results(audit_id):
    """Check what the API returns for analysis."""
    
    print(f"\n🌐 API Analysis Results Check")
    print("=" * 50)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if response.status_code == 200:
            data = response.json()['data']
            summary = data['analysis_summary']
            
            print(f"📈 API Analysis Summary:")
            print(f"   Total Rules: {summary['total_rules']}")
            print(f"   Total Objects: {summary['total_objects']}")
            print(f"   Used Objects: {summary['used_objects_count']}")
            print(f"   Unused Objects: {summary['unused_objects_count']}")
            
            # Check specific categories
            categories = ['duplicateRules', 'shadowedRules', 'unusedRules', 'overlappingRules', 'unusedObjects']
            
            print(f"\n📋 Analysis Categories:")
            for category in categories:
                items = data.get(category, [])
                print(f"   {category}: {len(items)} items")
                
                # Show details for unused objects
                if category == 'unusedObjects' and len(items) > 0:
                    print(f"      Sample unused objects:")
                    for i, obj in enumerate(items[:3]):
                        print(f"      {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')})")
            
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API check failed: {str(e)}")
        return False

def main():
    """Main verification function."""
    
    print("🔍 DEEP VERIFICATION OF PARSING AND ANALYSIS")
    print("=" * 60)
    
    # Step 1: Examine database content
    audit_id, rule_count, object_count = examine_database_content()
    
    if audit_id:
        # Step 2: Analyze object usage logic
        usage_correct = analyze_object_usage_logic(audit_id)
        
        # Step 3: Check API results
        api_correct = check_api_analysis_results(audit_id)
        
        # Summary
        print(f"\n📋 VERIFICATION SUMMARY")
        print("=" * 30)
        print(f"Audit ID: {audit_id}")
        print(f"Rules parsed: {rule_count}")
        print(f"Objects parsed: {object_count}")
        print(f"Usage analysis: {'✅ Correct' if usage_correct else '❌ Issues found'}")
        print(f"API results: {'✅ Working' if api_correct else '❌ Issues found'}")
        
        if not usage_correct:
            print(f"\n🔧 ISSUES IDENTIFIED:")
            print(f"   - Object usage analysis has discrepancies")
            print(f"   - Need to check the analyze_object_usage() function")
            print(f"   - May need to fix the object reference detection logic")
        
        return usage_correct and api_correct
    else:
        print(f"❌ Could not analyze - no recent audit found")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ VERIFICATION PASSED - System working correctly")
    else:
        print(f"\n❌ VERIFICATION FAILED - Issues found that need fixing")
