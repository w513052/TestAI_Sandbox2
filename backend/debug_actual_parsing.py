#!/usr/bin/env python3
"""
Debug the actual parsing by calling parse_set_config directly with our test content.
"""

def debug_actual_parsing():
    """Debug the actual parsing with our test content."""
    
    print("🔍 DEBUGGING ACTUAL PARSING")
    print("=" * 50)
    
    # Use the exact same content from our test file
    test_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32
set address Server-DB-01 ip-netmask 192.168.10.20/32

set rulebase security rules Allow-Web-Access from trust
set rulebase security rules Allow-Web-Access to untrust
set rulebase security rules Allow-Web-Access source Server-Web-01
set rulebase security rules Allow-Web-Access destination any
set rulebase security rules Allow-Web-Access service service-http
set rulebase security rules Allow-Web-Access action allow

set rulebase security rules Allow-DB-Access from trust
set rulebase security rules Allow-DB-Access to dmz
set rulebase security rules Allow-DB-Access source Server-DB-01
set rulebase security rules Allow-DB-Access destination any
set rulebase security rules Allow-DB-Access service service-mysql
set rulebase security rules Allow-DB-Access action allow"""
    
    try:
        from src.utils.parse_config import parse_set_config
        
        print(f"📋 Test Content:")
        lines = test_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                print(f"   {i+1:2d}. {line}")
        
        print(f"\n🧪 Calling parse_set_config...")
        rules_data, objects_data, metadata = parse_set_config(test_content)
        
        print(f"\n📊 Parsing Results:")
        print(f"   Rules parsed: {len(rules_data)}")
        print(f"   Objects parsed: {len(objects_data)}")
        print(f"   Metadata: {metadata}")
        
        print(f"\n📋 Rules Found:")
        for i, rule in enumerate(rules_data):
            print(f"   {i+1}. '{rule['rule_name']}'")
            print(f"      {rule['src_zone']} → {rule['dst_zone']} | {rule['src']} → {rule['dst']} | {rule['service']} | {rule['action']}")
            print(f"      Position: {rule['position']}, Disabled: {rule['is_disabled']}")
            print(f"      Raw: {rule['raw_xml'][:100]}...")
            print()
        
        print(f"\n📦 Objects Found:")
        for i, obj in enumerate(objects_data):
            print(f"   {i+1}. '{obj['name']}' = {obj['value']}")
        
        # Expected: 2 rules, 2 objects
        expected_rules = 2
        expected_objects = 2
        
        print(f"\n🎯 Expected vs Actual:")
        print(f"   Rules: Expected={expected_rules}, Actual={len(rules_data)} {'✅' if len(rules_data) == expected_rules else '❌'}")
        print(f"   Objects: Expected={expected_objects}, Actual={len(objects_data)} {'✅' if len(objects_data) == expected_objects else '❌'}")
        
        if len(rules_data) == expected_rules:
            print(f"\n✅ PARSING WORKS CORRECTLY!")
            print(f"   The issue must be with the uploaded file content or format")
            return True
        else:
            print(f"\n❌ PARSING IS BROKEN!")
            print(f"   Expected {expected_rules} consolidated rules, got {len(rules_data)}")
            
            # Debug why consolidation failed
            if len(rules_data) > expected_rules:
                print(f"\n🔍 Consolidation Failed - Analyzing Rule Names:")
                rule_names = [rule['rule_name'] for rule in rules_data]
                from collections import Counter
                name_counts = Counter(rule_names)
                
                for name, count in name_counts.items():
                    if count > 1:
                        print(f"      '{name}': {count} rules (should be consolidated)")
                    else:
                        print(f"      '{name}': {count} rule")
            
            return False
        
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def debug_with_larger_content():
    """Debug with content that matches the uploaded file size."""
    
    print(f"\n🔍 DEBUGGING WITH LARGER CONTENT")
    print("=" * 50)
    
    # Create content similar to the uploaded file (17 rules)
    large_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32
set address Server-DB-01 ip-netmask 192.168.10.20/32
set address Workstation-01 ip-netmask 192.168.20.10/32
set address Workstation-02 ip-netmask 192.168.20.11/32
set address DMZ-Host-01 ip-netmask 172.16.10.5/32
set address DMZ-Host-02 ip-netmask 172.16.10.6/32
set address External-Server-01 ip-netmask 203.0.113.10/32
set address Guest-Network ip-netmask 192.168.40.0/24
set address Internal-Subnet-01 ip-netmask 192.168.30.0/24
set address Internal-Subnet-02 ip-netmask 192.168.31.0/24
set address Backup-Server-01 ip-netmask 192.168.50.10/32
set address Monitoring-Host-01 ip-netmask 192.168.60.5/32
set address Server-Web-01-Redundant ip-netmask 192.168.10.10/32
set address Server-DB-01-Redundant ip-netmask 192.168.10.20/32
set address Internal-Subnet-01-Redundant ip-netmask 192.168.30.0/24
set address DMZ-Host-01-Redundant ip-netmask 172.16.10.5/32
set address Workstation-01-Redundant ip-netmask 192.168.20.10/32

set rulebase security rules Allow-Web-Access from trust
set rulebase security rules Allow-Web-Access to untrust
set rulebase security rules Allow-Web-Access source Server-Web-01
set rulebase security rules Allow-Web-Access destination any
set rulebase security rules Allow-Web-Access service service-http
set rulebase security rules Allow-Web-Access action allow

set rulebase security rules Allow-DB-Access from trust
set rulebase security rules Allow-DB-Access to dmz
set rulebase security rules Allow-DB-Access source Server-DB-01
set rulebase security rules Allow-DB-Access destination any
set rulebase security rules Allow-DB-Access service service-mysql
set rulebase security rules Allow-DB-Access action allow

set rulebase security rules Workstation-Outbound from trust
set rulebase security rules Workstation-Outbound to untrust
set rulebase security rules Workstation-Outbound source Workstation-01
set rulebase security rules Workstation-Outbound destination any
set rulebase security rules Workstation-Outbound service any
set rulebase security rules Workstation-Outbound action allow"""
    
    try:
        from src.utils.parse_config import parse_set_config
        
        print(f"📋 Large Content Test:")
        print(f"   Content length: {len(large_content)} characters")
        print(f"   Expected: 17 objects, 3 rules")
        
        rules_data, objects_data, metadata = parse_set_config(large_content)
        
        print(f"\n📊 Large Content Results:")
        print(f"   Rules parsed: {len(rules_data)}")
        print(f"   Objects parsed: {len(objects_data)}")
        
        print(f"\n📋 Rule Names:")
        for i, rule in enumerate(rules_data):
            print(f"   {i+1}. '{rule['rule_name']}'")
        
        expected_rules = 3
        expected_objects = 17
        
        print(f"\n🎯 Large Content Expected vs Actual:")
        print(f"   Rules: Expected={expected_rules}, Actual={len(rules_data)} {'✅' if len(rules_data) == expected_rules else '❌'}")
        print(f"   Objects: Expected={expected_objects}, Actual={len(objects_data)} {'✅' if len(objects_data) == expected_objects else '❌'}")
        
        return len(rules_data) == expected_rules and len(objects_data) == expected_objects
        
    except Exception as e:
        print(f"❌ Large content test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DEBUGGING ACTUAL PARSING BEHAVIOR")
    print("=" * 70)
    
    # Test with small content
    small_success = debug_actual_parsing()
    
    # Test with larger content
    large_success = debug_with_larger_content()
    
    print(f"\n📊 RESULTS:")
    print(f"   Small content test: {'✅ PASS' if small_success else '❌ FAIL'}")
    print(f"   Large content test: {'✅ PASS' if large_success else '❌ FAIL'}")
    
    if small_success and large_success:
        print(f"\n✅ PARSING FUNCTION WORKS CORRECTLY!")
        print(f"   The issue must be with the specific uploaded file content")
        print(f"   Or there's a different parsing path being used")
    else:
        print(f"\n❌ PARSING FUNCTION HAS ISSUES!")
        print(f"   The incremental parsing logic needs to be fixed")
