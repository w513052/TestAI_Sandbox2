#!/usr/bin/env python3
"""
Verify the output against the user's simple test breakdown.
"""

import requests
import sqlite3

def verify_simple_test_output():
    """Verify the output against the simple test breakdown."""
    
    print("🔍 VERIFYING SIMPLE TEST OUTPUT")
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
        print(f"📋 Most Recent Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        # Get analysis results from API
        analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()['data']
            summary = analysis_data['analysis_summary']
            
            print(f"\n📊 System Output:")
            print(f"   Total Rules: {summary['total_rules']}")
            print(f"   Total Objects: {summary['total_objects']}")
            print(f"   Used Objects: {summary['used_objects_count']}")
            print(f"   Unused Objects: {summary['unused_objects_count']}")
            print(f"   Redundant Objects: {summary.get('redundant_objects_count', 0)}")
            
            # Get detailed analysis
            unused_objects = analysis_data.get('unusedObjects', [])
            redundant_objects = analysis_data.get('redundantObjects', [])
            unused_rules = analysis_data.get('unusedRules', [])
            duplicate_rules = analysis_data.get('duplicateRules', [])
            
            print(f"\n📋 Detailed Analysis:")
            print(f"   Unused Rules: {len(unused_rules)}")
            print(f"   Duplicate Rules: {len(duplicate_rules)}")
            print(f"   Shadowed Rules: {len(analysis_data.get('shadowedRules', []))}")
            print(f"   Overlapping Rules: {len(analysis_data.get('overlappingRules', []))}")
            
            # Show specific unused objects
            print(f"\n📦 Unused Objects ({len(unused_objects)}):")
            for obj in unused_objects:
                print(f"   - {obj['name']} = {obj['value']}")
            
            # Show specific redundant objects
            print(f"\n🔄 Redundant Objects ({len(redundant_objects)}):")
            for obj in redundant_objects:
                print(f"   - {obj['name']} = {obj['value']}")
            
            # Show specific unused rules
            print(f"\n📋 Unused Rules ({len(unused_rules)}):")
            for rule in unused_rules[:5]:  # Show first 5
                print(f"   - {rule.get('name', 'N/A')}: {rule.get('description', 'N/A')}")
            
            # Show specific duplicate rules
            print(f"\n🔄 Duplicate Rules ({len(duplicate_rules)}):")
            for dup in duplicate_rules[:5]:  # Show first 5
                orig = dup.get('original_rule', {}).get('name', 'N/A')
                duplicate = dup.get('duplicate_rule', {}).get('name', 'N/A')
                print(f"   - {duplicate} duplicates {orig}")
            
            # Compare with user's expected breakdown
            print(f"\n🎯 USER'S EXPECTED vs SYSTEM OUTPUT:")
            
            expected = {
                "total_objects": 8,  # 5 original + 2 duplicate + 1 unused
                "total_rules": 8,    # 5 original + 2 duplicate + 1 unused
                "unused_objects": 1, # 1 unused object
                "duplicate_objects": 2, # 2 duplicate objects (redundant)
                "unused_rules": 1,   # 1 unused rule
                "duplicate_rules": 2 # 2 duplicate rules
            }
            
            actual = {
                "total_objects": summary['total_objects'],
                "total_rules": summary['total_rules'],
                "unused_objects": summary['unused_objects_count'],
                "duplicate_objects": summary.get('redundant_objects_count', 0),
                "unused_rules": len(unused_rules),
                "duplicate_rules": len(duplicate_rules)
            }
            
            print(f"\n📊 COMPARISON:")
            all_correct = True
            for key in expected:
                expected_val = expected[key]
                actual_val = actual[key]
                status = "✅" if actual_val == expected_val else "❌"
                print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                if actual_val != expected_val:
                    all_correct = False
            
            # Calculate accuracy
            correct_count = sum(1 for key in expected if actual[key] == expected[key])
            accuracy = (correct_count / len(expected)) * 100
            
            print(f"\n📈 ACCURACY: {accuracy:.1f}% ({correct_count}/{len(expected)} correct)")
            
            if all_correct:
                print(f"\n🎉 PERFECT MATCH!")
                print(f"   System output exactly matches your expected breakdown")
                print(f"   All analysis categories are correct")
            else:
                print(f"\n⚠️  DISCREPANCIES FOUND:")
                for key in expected:
                    if actual[key] != expected[key]:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        difference = actual_val - expected_val
                        print(f"   {key}: Off by {difference} ({'over' if difference > 0 else 'under'})")
            
            # Provide specific feedback
            print(f"\n💡 ANALYSIS:")
            
            if actual['total_objects'] == expected['total_objects'] and actual['total_rules'] == expected['total_rules']:
                print(f"   ✅ Core parsing is working correctly")
                print(f"   ✅ Total counts match expectations")
            else:
                print(f"   ❌ Core parsing has issues")
                print(f"   ❌ Total counts don't match")
            
            if actual['unused_objects'] == expected['unused_objects']:
                print(f"   ✅ Unused object detection is accurate")
            else:
                print(f"   ⚠️  Unused object detection needs adjustment")
            
            if actual['duplicate_objects'] == expected['duplicate_objects']:
                print(f"   ✅ Duplicate object detection is accurate")
            else:
                print(f"   ⚠️  Duplicate object detection needs adjustment")
            
            if actual['unused_rules'] == expected['unused_rules']:
                print(f"   ✅ Unused rule detection is accurate")
            else:
                print(f"   ⚠️  Unused rule detection needs adjustment")
            
            if actual['duplicate_rules'] == expected['duplicate_rules']:
                print(f"   ✅ Duplicate rule detection is accurate")
            else:
                print(f"   ⚠️  Duplicate rule detection needs adjustment")
            
            return all_correct
            
        else:
            print(f"❌ Analysis request failed: {analysis_response.status_code}")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFYING SIMPLE TEST OUTPUT")
    print("=" * 60)
    
    success = verify_simple_test_output()
    
    if success:
        print(f"\n🎉 VERIFICATION SUCCESSFUL!")
        print(f"   System output matches your expected breakdown")
        print(f"   All analysis categories are working correctly")
    else:
        print(f"\n⚠️  VERIFICATION FOUND DISCREPANCIES!")
        print(f"   Some analysis categories need adjustment")
    
    print(f"\n💡 SUMMARY:")
    print(f"   Your test breakdown is very clear and specific")
    print(f"   This helps identify exactly what needs to be fixed")
    print(f"   The system should match your expectations exactly")
