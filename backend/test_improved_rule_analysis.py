#!/usr/bin/env python3
"""
Test the improved rule analysis logic to see if it now works for both SET and XML formats.
"""

import requests

def test_improved_rule_analysis():
    """Test the improved rule analysis logic."""
    
    print("🧪 Testing Improved Rule Analysis Logic")
    print("=" * 50)
    
    try:
        # Test both SET and XML formats
        formats_to_test = [
            ("SET", "sample4-setcode_obj8.5.2.1-policy8.5.2.1.txt"),
            ("XML", "sample7-obj-policy8.5.2.1.xml")
        ]
        
        results = {}
        
        for format_type, filename_pattern in formats_to_test:
            print(f"\n🔧 Testing {format_type} Format:")
            
            # Get the most recent audit for this format
            response = requests.get('http://127.0.0.1:8000/api/v1/audits')
            if response.status_code == 200:
                audits = response.json()['data']
                
                # Find the audit for this format
                target_audit = None
                for audit in audits:
                    if filename_pattern in audit['filename']:
                        target_audit = audit
                        break
                
                if target_audit:
                    audit_id = target_audit['audit_id']
                    print(f"   Testing Audit {audit_id}: {target_audit['filename']}")
                    
                    # Get analysis results
                    analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                    
                    if analysis_response.status_code == 200:
                        analysis_data = analysis_response.json()['data']
                        summary = analysis_data['analysis_summary']
                        
                        print(f"   📊 {format_type} Analysis Results:")
                        print(f"      Total Rules: {summary['total_rules']}")
                        print(f"      Total Objects: {summary['total_objects']}")
                        print(f"      Used Objects: {summary['used_objects_count']}")
                        print(f"      Unused Objects: {summary['unused_objects_count']}")
                        print(f"      Redundant Objects: {summary.get('redundant_objects_count', 0)}")
                        
                        # Check detailed analysis
                        categories = {
                            'unusedRules': 'Unused Rules',
                            'duplicateRules': 'Duplicate Rules',
                            'shadowedRules': 'Shadowed Rules',
                            'overlappingRules': 'Overlapping Rules'
                        }
                        
                        print(f"   📋 {format_type} Rule Analysis:")
                        working_count = 0
                        
                        for key, name in categories.items():
                            items = analysis_data.get(key, [])
                            count = len(items) if items else 0
                            
                            if count > 0:
                                working_count += 1
                                print(f"      ✅ {name}: {count} items")
                                
                                # Show sample items
                                for i, item in enumerate(items[:2]):
                                    if key == 'duplicateRules':
                                        orig = item.get('original_rule', {}).get('name', 'N/A')
                                        dup = item.get('duplicate_rule', {}).get('name', 'N/A')
                                        print(f"         {i+1}. {dup} duplicates {orig}")
                                    else:
                                        name_field = item.get('name', item.get('rule_name', 'N/A'))
                                        print(f"         {i+1}. {name_field}")
                            else:
                                print(f"      ⚪ {name}: 0 items")
                        
                        results[format_type] = {
                            'working_categories': working_count,
                            'unused_rules': len(analysis_data.get('unusedRules', [])),
                            'duplicate_rules': len(analysis_data.get('duplicateRules', [])),
                            'shadowed_rules': len(analysis_data.get('shadowedRules', [])),
                            'overlapping_rules': len(analysis_data.get('overlappingRules', []))
                        }
                        
                        print(f"   📈 {format_type} Status: {working_count}/4 categories working")
                        
                    else:
                        print(f"   ❌ {format_type} Analysis failed: {analysis_response.status_code}")
                        results[format_type] = {'working_categories': 0}
                else:
                    print(f"   ❌ No {format_type} audit found")
                    results[format_type] = {'working_categories': 0}
            else:
                print(f"   ❌ Failed to get audits: {response.status_code}")
                results[format_type] = {'working_categories': 0}
        
        # Compare results
        print(f"\n📊 IMPROVEMENT COMPARISON:")
        print("=" * 40)
        
        for format_type in ['SET', 'XML']:
            if format_type in results:
                result = results[format_type]
                working = result['working_categories']
                
                # Previous status
                if format_type == 'SET':
                    previous_working = 0  # Was completely broken
                    expected_working = 2  # Should detect unused and duplicate rules
                else:  # XML
                    previous_working = 2  # Was partially working (unused, overlapping)
                    expected_working = 4  # Should detect all categories
                
                improvement = working - previous_working
                
                print(f"{format_type} Format:")
                print(f"   Previous: {previous_working}/4 categories working")
                print(f"   Current:  {working}/4 categories working")
                print(f"   Expected: {expected_working}/4 categories working")
                print(f"   Improvement: {'+' if improvement > 0 else ''}{improvement} categories")
                
                if working >= expected_working:
                    print(f"   Status: ✅ FULLY FIXED!")
                elif improvement > 0:
                    print(f"   Status: 🔧 IMPROVED!")
                else:
                    print(f"   Status: ❌ Still broken")
                
                # Show specific results
                if working > 0:
                    print(f"   Details:")
                    if result.get('unused_rules', 0) > 0:
                        print(f"      ✅ Unused Rules: {result['unused_rules']}")
                    if result.get('duplicate_rules', 0) > 0:
                        print(f"      ✅ Duplicate Rules: {result['duplicate_rules']}")
                    if result.get('shadowed_rules', 0) > 0:
                        print(f"      ✅ Shadowed Rules: {result['shadowed_rules']}")
                    if result.get('overlapping_rules', 0) > 0:
                        print(f"      ✅ Overlapping Rules: {result['overlapping_rules']}")
                
                print()
        
        # Overall assessment
        total_improvement = sum(results[fmt]['working_categories'] for fmt in results)
        previous_total = 2  # XML was partially working
        
        print(f"📈 OVERALL IMPROVEMENT:")
        print(f"   Previous total: {previous_total} working categories")
        print(f"   Current total:  {total_improvement} working categories")
        print(f"   Net improvement: +{total_improvement - previous_total} categories")
        
        if total_improvement >= 6:  # Both formats mostly working
            print(f"   🎉 MAJOR SUCCESS! Both formats significantly improved")
            return True
        elif total_improvement > previous_total:
            print(f"   🔧 GOOD PROGRESS! Analysis logic improved")
            return True
        else:
            print(f"   ⚠️  Limited improvement, more work needed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING IMPROVED RULE ANALYSIS LOGIC")
    print("=" * 70)
    
    success = test_improved_rule_analysis()
    
    if success:
        print(f"\n🎉 RULE ANALYSIS LOGIC SIGNIFICANTLY IMPROVED!")
        print(f"   Both SET and XML formats should now work better")
        print(f"   Frontend should show more accurate analysis counts")
    else:
        print(f"\n⚠️  RULE ANALYSIS STILL NEEDS MORE WORK!")
        print(f"   Some improvements made but not fully fixed")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test in frontend with both SET and XML files")
    print(f"   2. Verify analysis tabs show proper counts")
    print(f"   3. Check that duplicate and shadowed rules are detected")
    print(f"   4. Ensure unused rules are properly identified")
