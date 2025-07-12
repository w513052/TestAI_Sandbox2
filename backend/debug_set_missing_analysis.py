#!/usr/bin/env python3
"""
Debug why overlapping rules and unused objects are still not working for SET command format.
"""

import requests
import sqlite3

def debug_set_missing_analysis():
    """Debug the missing analysis for SET format."""
    
    print("🔍 DEBUGGING SET FORMAT MISSING ANALYSIS")
    print("=" * 50)
    
    try:
        # Get the SET format audit
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM audit_sessions 
            WHERE filename LIKE '%sample4%'
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        set_audit = cursor.fetchone()
        if not set_audit:
            print("❌ SET format audit not found")
            return
        
        audit_id = set_audit[0]
        print(f"📋 Debugging SET Audit {audit_id}")
        
        # Check objects in database
        cursor.execute("""
            SELECT name, object_type, value, used_in_rules
            FROM object_definitions 
            WHERE audit_id = ?
            ORDER BY name
        """, (audit_id,))
        
        objects = cursor.fetchall()
        
        print(f"\n📦 Objects in Database ({len(objects)}):")
        unused_objects_manual = []
        for obj in objects:
            name, obj_type, value, used_in_rules = obj
            status = "USED" if used_in_rules > 0 else "UNUSED"
            print(f"   {name} ({obj_type}) = {value} | {status} ({used_in_rules} rules)")
            if used_in_rules == 0:
                unused_objects_manual.append(name)
        
        print(f"\n🔍 Manual Unused Object Detection:")
        print(f"   Found {len(unused_objects_manual)} unused objects: {unused_objects_manual}")
        
        # Check rules in database
        cursor.execute("""
            SELECT rule_name, src_zone, dst_zone, src, dst, service, action, position, is_disabled
            FROM firewall_rules 
            WHERE audit_id = ?
            ORDER BY position
        """, (audit_id,))
        
        rules = cursor.fetchall()
        
        print(f"\n📋 Rules in Database ({len(rules)}):")
        for i, rule in enumerate(rules):
            rule_name, src_zone, dst_zone, src, dst, service, action, position, is_disabled = rule
            status = "DISABLED" if is_disabled else "ENABLED"
            print(f"   {i+1}. {rule_name} | {src_zone}→{dst_zone} | {src}→{dst} | {service} | {action} | {status}")
        
        conn.close()
        
        # Get API analysis results
        analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()['data']
            summary = analysis_data['analysis_summary']
            
            print(f"\n📊 API Analysis Results:")
            print(f"   Unused Objects Count: {summary.get('unused_objects_count', 'MISSING')}")
            print(f"   Overlapping Rules Count: {len(analysis_data.get('overlappingRules', []))}")
            
            # Check unused objects from API
            unused_objects_api = analysis_data.get('unusedObjects', [])
            print(f"\n📦 API Unused Objects ({len(unused_objects_api)}):")
            for obj in unused_objects_api:
                print(f"   - {obj.get('name', 'N/A')} = {obj.get('value', 'N/A')}")
            
            # Check overlapping rules from API
            overlapping_rules_api = analysis_data.get('overlappingRules', [])
            print(f"\n🔄 API Overlapping Rules ({len(overlapping_rules_api)}):")
            for rule in overlapping_rules_api:
                rule1 = rule.get('rule1', {}).get('name', 'N/A')
                rule2 = rule.get('rule2', {}).get('name', 'N/A')
                print(f"   - {rule1} overlaps {rule2}")
            
            # Compare manual vs API results
            print(f"\n🎯 Manual vs API Comparison:")
            print(f"   Unused Objects:")
            print(f"      Manual: {len(unused_objects_manual)} ({unused_objects_manual})")
            print(f"      API: {len(unused_objects_api)} ({[obj.get('name') for obj in unused_objects_api]})")
            
            if len(unused_objects_manual) > 0 and len(unused_objects_api) == 0:
                print(f"      🚨 ISSUE: Manual finds unused objects but API doesn't!")
                print(f"      Problem: Object usage analysis logic is broken")
            
            # Manual overlapping rule detection
            print(f"\n🔍 Manual Overlapping Rule Detection:")
            overlapping_manual = detect_overlapping_rules_manual(rules)
            print(f"   Manual: {len(overlapping_manual)} overlapping pairs")
            print(f"   API: {len(overlapping_rules_api)} overlapping pairs")
            
            if len(overlapping_manual) > 0 and len(overlapping_rules_api) == 0:
                print(f"      🚨 ISSUE: Manual finds overlapping rules but API doesn't!")
                print(f"      Problem: Overlapping rule analysis logic is broken")
            
            return {
                'unused_objects_manual': len(unused_objects_manual),
                'unused_objects_api': len(unused_objects_api),
                'overlapping_rules_manual': len(overlapping_manual),
                'overlapping_rules_api': len(overlapping_rules_api)
            }
            
        else:
            print(f"❌ Analysis request failed: {analysis_response.status_code}")
            return None
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def detect_overlapping_rules_manual(rules):
    """Manually detect overlapping rules."""
    
    overlapping = []
    
    for i, rule1 in enumerate(rules):
        for j, rule2 in enumerate(rules):
            if i >= j:  # Avoid duplicates and self-comparison
                continue
            
            rule1_name, src_zone1, dst_zone1, src1, dst1, service1, action1, pos1, disabled1 = rule1
            rule2_name, src_zone2, dst_zone2, src2, dst2, service2, action2, pos2, disabled2 = rule2
            
            # Skip disabled rules
            if disabled1 or disabled2:
                continue
            
            # Check if rules overlap (simple check)
            if (action1 == action2 and
                (src_zone1 == src_zone2 or src_zone1 == 'any' or src_zone2 == 'any') and
                (dst_zone1 == dst_zone2 or dst_zone1 == 'any' or dst_zone2 == 'any') and
                (src1 == src2 or src1 == 'any' or src2 == 'any') and
                (dst1 == dst2 or dst1 == 'any' or dst2 == 'any')):
                
                overlapping.append((rule1_name, rule2_name))
                print(f"   OVERLAP: {rule1_name} overlaps {rule2_name}")
    
    return overlapping

def suggest_fixes(results):
    """Suggest fixes for the missing analysis."""
    
    if not results:
        return
    
    print(f"\n🔧 SUGGESTED FIXES:")
    print("=" * 30)
    
    if results['unused_objects_manual'] > 0 and results['unused_objects_api'] == 0:
        print(f"1. **Unused Object Detection Broken:**")
        print(f"   - Manual detection finds {results['unused_objects_manual']} unused objects")
        print(f"   - API detection finds 0 unused objects")
        print(f"   - Issue: Object categorization logic in analysis endpoint")
        print(f"   - Fix: Check object usage analysis in audits/__init__.py")
    
    if results['overlapping_rules_manual'] > 0 and results['overlapping_rules_api'] == 0:
        print(f"\n2. **Overlapping Rule Detection Broken:**")
        print(f"   - Manual detection finds {results['overlapping_rules_manual']} overlapping rules")
        print(f"   - API detection finds 0 overlapping rules")
        print(f"   - Issue: Overlapping rule analysis logic")
        print(f"   - Fix: Check overlapping rule detection in rule_analysis.py")
    
    print(f"\n3. **SET Format Specific Issues:**")
    print(f"   - SET format may have different data structure")
    print(f"   - Analysis logic may not handle SET format properly")
    print(f"   - Need to ensure analysis works for both XML and SET")

if __name__ == "__main__":
    print("🚀 DEBUGGING SET FORMAT MISSING ANALYSIS")
    print("=" * 60)
    
    results = debug_set_missing_analysis()
    
    if results:
        suggest_fixes(results)
        
        print(f"\n💡 SUMMARY:")
        print(f"   SET format has specific issues with:")
        print(f"   - Unused object detection (manual finds objects, API doesn't)")
        print(f"   - Overlapping rule detection (manual finds overlaps, API doesn't)")
        print(f"   Both suggest analysis pipeline issues for SET format")
    else:
        print(f"\n❌ Could not debug SET format analysis issues")
    
    print(f"\n🎯 PRIORITY FIXES:")
    print(f"   1. Fix unused object categorization for SET format")
    print(f"   2. Fix overlapping rule detection for SET format")
    print(f"   3. Ensure analysis pipeline works consistently for both formats")
