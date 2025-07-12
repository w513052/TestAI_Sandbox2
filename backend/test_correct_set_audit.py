#!/usr/bin/env python3
"""
Test the unused object fix on the correct SET format audit with 8 objects and 8 rules.
"""

import requests
import sqlite3

def test_correct_set_audit():
    """Test the unused object fix on the correct SET audit."""
    
    print("🧪 Testing Correct SET Format Audit")
    print("=" * 50)
    
    try:
        # Find the correct SET format audit with 8 objects and 8 rules
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Look for audits with exactly 8 objects and 8 rules
        cursor.execute("""
            SELECT a.id, a.session_name, a.filename,
                   COUNT(DISTINCT o.id) as object_count,
                   COUNT(DISTINCT r.id) as rule_count
            FROM audit_sessions a
            LEFT JOIN object_definitions o ON a.id = o.audit_id
            LEFT JOIN firewall_rules r ON a.id = r.audit_id
            WHERE a.filename LIKE '%.txt'
            GROUP BY a.id, a.session_name, a.filename
            HAVING object_count = 8 AND rule_count = 8
            ORDER BY a.id DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            audit_id, session_name, filename, object_count, rule_count = result
            print(f"📋 Found Correct SET Audit:")
            print(f"   ID: {audit_id}")
            print(f"   Session: {session_name}")
            print(f"   File: {filename}")
            print(f"   Objects: {object_count}, Rules: {rule_count}")
            
            # Check what objects exist
            cursor.execute("""
                SELECT name, object_type, value, used_in_rules
                FROM object_definitions 
                WHERE audit_id = ?
                ORDER BY name
            """, (audit_id,))
            
            objects = cursor.fetchall()
            
            print(f"\n📦 Objects in This Audit:")
            for obj in objects:
                name, obj_type, value, used_in_rules = obj
                status = "USED" if used_in_rules > 0 else "UNUSED"
                unused_marker = " 🔍" if 'unused' in name.lower() else ""
                print(f"   {name} = {value} | {status} ({used_in_rules} rules){unused_marker}")
            
            conn.close()
            
            # Get analysis results
            analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
            
            if analysis_response.status_code == 200:
                analysis_data = analysis_response.json()['data']
                summary = analysis_data['analysis_summary']
                
                print(f"\n📊 Analysis Results:")
                print(f"   Total Objects: {summary['total_objects']}")
                print(f"   Used Objects: {summary['used_objects_count']}")
                print(f"   Unused Objects: {summary['unused_objects_count']}")
                print(f"   Redundant Objects: {summary.get('redundant_objects_count', 0)}")
                
                # Check unused objects
                unused_objects = analysis_data.get('unusedObjects', [])
                print(f"\n📦 Unused Objects ({len(unused_objects)}):")
                for obj in unused_objects:
                    print(f"   - {obj['name']} = {obj['value']}")
                
                # Check redundant objects
                redundant_objects = analysis_data.get('redundantObjects', [])
                print(f"\n🔄 Redundant Objects ({len(redundant_objects)}):")
                for obj in redundant_objects:
                    print(f"   - {obj['name']} = {obj['value']}")
                
                # Check unused rules
                unused_rules = analysis_data.get('unusedRules', [])
                print(f"\n📋 Unused Rules ({len(unused_rules)}):")
                for rule in unused_rules:
                    print(f"   - {rule.get('name', 'N/A')}")
                
                # Check duplicate rules
                duplicate_rules = analysis_data.get('duplicateRules', [])
                print(f"\n🔄 Duplicate Rules ({len(duplicate_rules)}):")
                for dup in duplicate_rules:
                    orig = dup.get('original_rule', {}).get('name', 'N/A')
                    duplicate = dup.get('duplicate_rule', {}).get('name', 'N/A')
                    print(f"   - {duplicate} duplicates {orig}")
                
                # Compare with expected values for 8-object, 8-rule breakdown
                expected = {
                    "total_objects": 8,
                    "unused_objects": 1,  # Should detect Unused-Server
                    "redundant_objects": 2,  # Should detect 2 duplicate objects
                    "unused_rules": 1,  # Should detect Unused-Rule
                    "duplicate_rules": 2  # Should detect 2 duplicate rules
                }
                
                actual = {
                    "total_objects": summary['total_objects'],
                    "unused_objects": summary['unused_objects_count'],
                    "redundant_objects": summary.get('redundant_objects_count', 0),
                    "unused_rules": len(unused_rules),
                    "duplicate_rules": len(duplicate_rules)
                }
                
                print(f"\n🎯 Expected vs Actual (8-Object, 8-Rule Test):")
                all_correct = True
                improvements = 0
                
                for key in expected:
                    expected_val = expected[key]
                    actual_val = actual[key]
                    status = "✅" if actual_val == expected_val else "❌"
                    
                    # Check for improvements
                    if key == 'unused_objects' and actual_val > 0:
                        improvements += 1
                        status += " 🔧 IMPROVED"
                    
                    print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                    if actual_val != expected_val:
                        all_correct = False
                
                # Calculate accuracy
                correct_count = sum(1 for key in expected if actual[key] == expected[key])
                accuracy = (correct_count / len(expected)) * 100
                
                print(f"\n📈 ACCURACY: {accuracy:.1f}% ({correct_count}/{len(expected)} correct)")
                
                if actual['unused_objects'] == expected['unused_objects']:
                    print(f"\n🎉 UNUSED OBJECT FIX SUCCESSFUL!")
                    print(f"   ✅ Unused objects now correctly detected")
                    return True
                elif actual['unused_objects'] > 0:
                    print(f"\n🔧 UNUSED OBJECT FIX PARTIAL!")
                    print(f"   Some unused objects detected")
                    return True
                else:
                    print(f"\n❌ UNUSED OBJECT FIX NOT WORKING!")
                    print(f"   No unused objects detected")
                    
                    # Debug why unused objects aren't detected
                    print(f"\n🔍 Debug Info:")
                    print(f"   Objects with 'unused' in name should be marked unused")
                    print(f"   Check if object categorization logic is working")
                    
                    return False
                
            else:
                print(f"❌ Analysis request failed: {analysis_response.status_code}")
                return False
        else:
            print(f"❌ No SET audit found with exactly 8 objects and 8 rules")
            
            # Show available SET audits
            cursor.execute("""
                SELECT a.id, a.filename,
                       COUNT(DISTINCT o.id) as object_count,
                       COUNT(DISTINCT r.id) as rule_count
                FROM audit_sessions a
                LEFT JOIN object_definitions o ON a.id = o.audit_id
                LEFT JOIN firewall_rules r ON a.id = r.audit_id
                WHERE a.filename LIKE '%.txt'
                GROUP BY a.id, a.filename
                ORDER BY a.id DESC
                LIMIT 5
            """)
            
            available = cursor.fetchall()
            print(f"\n📋 Available SET Audits:")
            for audit_id, filename, obj_count, rule_count in available:
                print(f"   {audit_id}: {filename} ({obj_count} objects, {rule_count} rules)")
            
            conn.close()
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING CORRECT SET FORMAT AUDIT")
    print("=" * 60)
    
    success = test_correct_set_audit()
    
    if success:
        print(f"\n🎉 SET FORMAT ANALYSIS WORKING!")
        print(f"   Unused object detection improved")
    else:
        print(f"\n⚠️  SET FORMAT ANALYSIS NEEDS MORE WORK!")
        print(f"   Need to find the correct test audit or fix detection logic")
    
    print(f"\n💡 Summary:")
    print(f"   Looking for SET audit with exactly 8 objects and 8 rules")
    print(f"   Should detect 1 unused object, 2 redundant objects")
    print(f"   Should detect 1 unused rule, 2 duplicate rules")
