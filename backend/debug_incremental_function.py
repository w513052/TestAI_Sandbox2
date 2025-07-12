#!/usr/bin/env python3
"""
Debug the incremental parsing function directly to see why it's not working.
"""

def test_incremental_function_directly():
    """Test the incremental parsing function directly."""
    
    print("🔍 TESTING INCREMENTAL FUNCTION DIRECTLY")
    print("=" * 50)
    
    try:
        from src.utils.parse_config import parse_incremental_set_rule
        
        # Test with a simple case
        rules_dict = {}
        
        test_lines = [
            "set rulebase security rules Allow-Web-Access from trust",
            "set rulebase security rules Allow-Web-Access to untrust", 
            "set rulebase security rules Allow-Web-Access source Server-Web-01",
            "set rulebase security rules Allow-Web-Access destination any",
            "set rulebase security rules Allow-Web-Access service service-http",
            "set rulebase security rules Allow-Web-Access action allow"
        ]
        
        print(f"📋 Test Lines:")
        for i, line in enumerate(test_lines):
            print(f"   {i+1}. {line}")
        
        print(f"\n🧪 Processing with parse_incremental_set_rule...")
        
        for line in test_lines:
            print(f"\n   Processing: {line}")
            parse_incremental_set_rule(line, rules_dict)
            print(f"   Rules dict now has {len(rules_dict)} rules")
            for name, rule_data in rules_dict.items():
                print(f"      '{name}': {rule_data['src_zone']} → {rule_data['dst_zone']} | {rule_data['src']} → {rule_data['dst']} | {rule_data['service']} | {rule_data['action']}")
        
        print(f"\n📊 Final Results:")
        print(f"   Rules created: {len(rules_dict)}")
        
        if len(rules_dict) == 1:
            rule_name, rule_data = list(rules_dict.items())[0]
            print(f"   ✅ Successfully consolidated into 1 rule: '{rule_name}'")
            print(f"      From: {rule_data['src_zone']} To: {rule_data['dst_zone']}")
            print(f"      Source: {rule_data['src']} Destination: {rule_data['dst']}")
            print(f"      Service: {rule_data['service']} Action: {rule_data['action']}")
            return True
        else:
            print(f"   ❌ Failed to consolidate - created {len(rules_dict)} rules instead of 1")
            for name, rule_data in rules_dict.items():
                print(f"      '{name}': incomplete rule")
            return False
        
    except Exception as e:
        print(f"❌ Direct function test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_name_extraction():
    """Test the rule name extraction logic."""
    
    print(f"\n🔍 TESTING RULE NAME EXTRACTION")
    print("=" * 50)
    
    test_cases = [
        "set rulebase security rules Allow-Web-Access from trust",
        "set rulebase security rules Allow-Web-Access to untrust",
        "set rulebase security rules Allow-Web-Access source Server-Web-01",
        "set rulebase security rules Allow-Web-Access destination any",
        "set rulebase security rules Allow-Web-Access service service-http",
        "set rulebase security rules Allow-Web-Access action allow"
    ]
    
    try:
        import re
        
        for line in test_cases:
            print(f"\n   Line: {line}")
            
            # Test the regex pattern from the function
            name_match = re.search(r'set (?:rulebase )?security rules ["\']?([^"\']+?)["\']?\s+(?:from|to|source|destination|service|action|application)', line)
            if name_match:
                rule_name = name_match.group(1).strip()
                print(f"   ✅ Extracted name: '{rule_name}'")
            else:
                print(f"   ❌ Failed to extract name with primary regex")
                
                # Try fallback
                name_match = re.search(r'set (?:rulebase )?security rules ["\']?([^"\']+)["\']?', line)
                if name_match:
                    full_name = name_match.group(1).strip()
                    print(f"   Fallback full name: '{full_name}'")
                    
                    # Clean the rule name by removing attribute keywords
                    attribute_keywords = ['from', 'to', 'source', 'destination', 'service', 'action', 'application']
                    rule_name = full_name
                    for keyword in attribute_keywords:
                        if ' ' + keyword + ' ' in ' ' + full_name + ' ':
                            rule_name = full_name.split(' ' + keyword)[0].strip()
                            print(f"   ✅ Cleaned name: '{rule_name}' (removed '{keyword}')")
                            break
                else:
                    print(f"   ❌ Failed to extract name with fallback regex")
        
        return True
        
    except Exception as e:
        print(f"❌ Rule name extraction test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DEBUGGING INCREMENTAL PARSING FUNCTION")
    print("=" * 70)
    
    # Test rule name extraction
    name_success = test_rule_name_extraction()
    
    # Test the incremental function
    func_success = test_incremental_function_directly()
    
    print(f"\n📊 RESULTS:")
    print(f"   Rule name extraction: {'✅ PASS' if name_success else '❌ FAIL'}")
    print(f"   Incremental function: {'✅ PASS' if func_success else '❌ FAIL'}")
    
    if name_success and func_success:
        print(f"\n✅ INCREMENTAL PARSING FUNCTION WORKS!")
        print(f"   The issue must be elsewhere in the parsing pipeline")
    else:
        print(f"\n❌ INCREMENTAL PARSING FUNCTION HAS ISSUES!")
        print(f"   Need to fix the function logic")
