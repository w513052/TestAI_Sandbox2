#!/usr/bin/env python3
"""
Test the fixed analysis logic on the correct audit (the simple 8-object, 8-rule test).
"""

import requests
import sqlite3

def test_correct_audit():
    """Test the fixed analysis logic on the correct audit."""
    
    print("🧪 Testing Fixed Analysis Logic on Correct Audit")
    print("=" * 50)
    
    try:
        # Get the correct audit (the simple test with 8 objects, 8 rules)
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Look for the audit with the simple test file
        cursor.execute("""
            SELECT id, session_name, filename 
            FROM audit_sessions 
            WHERE filename LIKE '%sample4%' OR session_name LIKE '%sample4%'
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ Simple test audit not found")
            return False, 0
        
        audit_id, session_name, filename = audit
        print(f"📋 Testing Correct Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        conn.close()
        
        # Get the analysis data with fixed logic
        analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()['data']
            summary = analysis_data['analysis_summary']
            
            print(f"\n📊 Fixed Analysis Results:")
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
            
            print(f"\n📋 Detailed Fixed Analysis:")
            print(f"   Unused Rules: {len(unused_rules)}")
            print(f"   Duplicate Rules: {len(duplicate_rules)}")
            print(f"   Shadowed Rules: {len(analysis_data.get('shadowedRules', []))}")
            print(f"   Overlapping Rules: {len(analysis_data.get('overlappingRules', []))}")
            
            # Show specific results
            print(f"\n📦 Unused Objects ({len(unused_objects)}):")
            for obj in unused_objects:
                print(f"   - {obj['name']} = {obj['value']}")
            
            print(f"\n🔄 Redundant Objects ({len(redundant_objects)}):")
            for obj in redundant_objects:
                print(f"   - {obj['name']} = {obj['value']}")
            
            print(f"\n📋 Unused Rules ({len(unused_rules)}):")
            for rule in unused_rules:
                print(f"   - {rule.get('name', 'N/A')}: {rule.get('description', 'N/A')}")
            
            print(f"\n🔄 Duplicate Rules ({len(duplicate_rules)}):")
            for dup in duplicate_rules:
                orig = dup.get('original_rule', {}).get('name', 'N/A')
                duplicate = dup.get('duplicate_rule', {}).get('name', 'N/A')
                print(f"   - {duplicate} duplicates {orig}")
            
            # Compare with expected values for the simple test
            expected = {
                "total_objects": 8,  # 5 original + 2 duplicate + 1 unused
                "total_rules": 8,    # 5 original + 2 duplicate + 1 unused
                "unused_objects": 1, # Unused-Server
                "redundant_objects": 2, # Database-Server-Dup, Web-Server-Dup
                "unused_rules": 1,   # Unused-Rule
                "duplicate_rules": 2 # Allow-Web-Dup, Allow-Database-Dup
            }
            
            actual = {
                "total_objects": summary['total_objects'],
                "total_rules": summary['total_rules'],
                "unused_objects": summary['unused_objects_count'],
                "redundant_objects": summary.get('redundant_objects_count', 0),
                "unused_rules": len(unused_rules),
                "duplicate_rules": len(duplicate_rules)
            }
            
            print(f"\n🎯 Expected vs Fixed Analysis (Simple Test):")
            all_correct = True
            improvements = 0
            previous_values = {
                "redundant_objects": 0,  # Was 0 before fix
                "unused_rules": 0        # Was 0 before fix
            }
            
            for key in expected:
                expected_val = expected[key]
                actual_val = actual[key]
                status = "✅" if actual_val == expected_val else "❌"
                
                # Check if this is an improvement from before
                if key in previous_values and actual_val > previous_values[key]:
                    improvements += 1
                    status += " 🔧 IMPROVED"
                
                print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                if actual_val != expected_val:
                    all_correct = False
            
            # Calculate accuracy
            correct_count = sum(1 for key in expected if actual[key] == expected[key])
            accuracy = (correct_count / len(expected)) * 100
            
            print(f"\n📈 ACCURACY: {accuracy:.1f}% ({correct_count}/{len(expected)} correct)")
            print(f"📈 IMPROVEMENTS: {improvements} categories now detecting issues")
            
            if all_correct:
                print(f"\n🎉 PERFECT! ANALYSIS LOGIC COMPLETELY FIXED!")
                print(f"   All categories match expected values exactly")
                print(f"   System now correctly detects:")
                print(f"   ✅ 2 redundant objects (Database-Server-Dup, Web-Server-Dup)")
                print(f"   ✅ 1 unused object (Unused-Server)")
                print(f"   ✅ 1 unused rule (Unused-Rule)")
                print(f"   ✅ 2 duplicate rules")
            elif improvements > 0:
                print(f"\n🔧 SIGNIFICANT IMPROVEMENT!")
                print(f"   Fixed {improvements} analysis categories")
                print(f"   System now detects issues that were missed before")
                
                # Show what still needs work
                for key in expected:
                    if actual[key] != expected[key]:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        difference = actual_val - expected_val
                        print(f"   Still needs work: {key} (off by {difference})")
            else:
                print(f"\n⚠️  ANALYSIS STILL HAS ISSUES")
                print(f"   No improvements detected")
            
            return all_correct, improvements
            
        else:
            print(f"❌ Analysis request failed: {analysis_response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False, 0

if __name__ == "__main__":
    print("🚀 TESTING FIXED ANALYSIS LOGIC ON CORRECT AUDIT")
    print("=" * 70)
    
    success, improvements = test_correct_audit()
    
    if success:
        print(f"\n🎉 ANALYSIS LOGIC COMPLETELY FIXED!")
        print(f"   All detection categories working perfectly")
        print(f"   Frontend will now show correct numbers")
        print(f"   Your simple test breakdown is perfectly matched")
    elif improvements > 0:
        print(f"\n🔧 ANALYSIS LOGIC SIGNIFICANTLY IMPROVED!")
        print(f"   {improvements} categories now working")
        print(f"   Major progress made on your simple test")
    else:
        print(f"\n💥 ANALYSIS LOGIC STILL BROKEN!")
        print(f"   Need further investigation")
    
    print(f"\n💡 Summary:")
    print(f"   Your simple test breakdown:")
    print(f"   - 8 total objects (5 original + 2 duplicate + 1 unused)")
    print(f"   - 8 total rules (5 original + 2 duplicate + 1 unused)")
    print(f"   - Should detect 2 redundant objects, 1 unused object, 1 unused rule")
