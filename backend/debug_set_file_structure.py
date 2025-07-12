#!/usr/bin/env python3
"""
Debug the actual set file structure to understand parsing issues.
"""

import sqlite3
import requests

def debug_set_file_structure():
    """Debug the set file structure and parsing."""
    
    print("🔍 DEBUGGING SET FILE STRUCTURE")
    print("=" * 50)
    
    try:
        # Get the most recent audit
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_name, filename, file_content
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ No audit sessions found")
            return
        
        audit_id, session_name, filename, file_content = audit
        print(f"📋 Most Recent Audit:")
        print(f"   ID: {audit_id}")
        print(f"   Session: {session_name}")
        print(f"   File: {filename}")
        
        # Decode and examine file content
        if file_content:
            try:
                content = file_content.decode('utf-8') if isinstance(file_content, bytes) else file_content
                lines = content.split('\n')
                
                print(f"\n📄 File Content Analysis:")
                print(f"   Total lines: {len(lines)}")
                print(f"   File size: {len(content)} characters")
                
                # Show first 20 lines
                print(f"\n📋 First 20 Lines:")
                for i, line in enumerate(lines[:20]):
                    line = line.strip()
                    if line:
                        print(f"   {i+1:2d}. {line}")
                
                # Analyze set command patterns
                print(f"\n🔍 Set Command Analysis:")
                
                address_lines = [line for line in lines if 'set address' in line.lower()]
                service_lines = [line for line in lines if 'set service' in line.lower()]
                rule_lines = [line for line in lines if 'set rulebase security rules' in line.lower() or 'set security rules' in line.lower()]
                
                print(f"   Address object lines: {len(address_lines)}")
                print(f"   Service object lines: {len(service_lines)}")
                print(f"   Security rule lines: {len(rule_lines)}")
                
                # Show sample address objects
                if address_lines:
                    print(f"\n📦 Sample Address Objects:")
                    for i, line in enumerate(address_lines[:5]):
                        print(f"   {i+1}. {line.strip()}")
                
                # Show sample service objects
                if service_lines:
                    print(f"\n🔧 Sample Service Objects:")
                    for i, line in enumerate(service_lines[:5]):
                        print(f"   {i+1}. {line.strip()}")
                
                # Show sample rules
                if rule_lines:
                    print(f"\n📋 Sample Security Rules:")
                    for i, line in enumerate(rule_lines[:5]):
                        print(f"   {i+1}. {line.strip()}")
                
                # Check if this is a different set format
                print(f"\n🔍 Set Format Analysis:")
                
                # Check for different set command patterns
                patterns = {
                    'Standard set address': len([l for l in lines if l.strip().startswith('set address')]),
                    'Standard set service': len([l for l in lines if l.strip().startswith('set service')]),
                    'Standard set security rules': len([l for l in lines if l.strip().startswith('set security rules')]),
                    'Rulebase set security rules': len([l for l in lines if l.strip().startswith('set rulebase security rules')]),
                    'Multi-line commands': len([l for l in lines if 'set' in l and len(l) > 200])
                }
                
                for pattern, count in patterns.items():
                    print(f"   {pattern}: {count} lines")
                
                # Check if commands are on single lines or split across multiple lines
                long_lines = [line for line in lines if len(line) > 200]
                if long_lines:
                    print(f"\n⚠️  Found {len(long_lines)} very long lines (>200 chars)")
                    print(f"   This suggests commands might be concatenated or malformed")
                    print(f"   Sample long line: {long_lines[0][:100]}...")
                
                return content
                
            except Exception as e:
                print(f"❌ Error decoding file content: {str(e)}")
                return None
        else:
            print(f"❌ No file content found in database")
            return None
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

def test_set_parsing_with_sample():
    """Test set parsing with a known good sample."""
    
    print(f"\n🧪 Testing Set Parsing with Known Sample")
    print("=" * 50)
    
    # Create a sample that matches the expected structure
    sample_content = """set address "Server-Web-01" ip-netmask 192.168.10.10/32
set address "Server-DB-01" ip-netmask 192.168.10.20/32
set address "Workstation-01" ip-netmask 192.168.20.10/32
set address "Workstation-02" ip-netmask 192.168.20.11/32
set address "DMZ-Host-01" ip-netmask 172.16.10.5/32
set address "DMZ-Host-02" ip-netmask 172.16.10.6/32
set address "External-Server-01" ip-netmask 203.0.113.10/32
set address "Guest-Network" ip-netmask 192.168.40.0/24
set address "Internal-Subnet-01" ip-netmask 192.168.30.0/24
set address "Internal-Subnet-02" ip-netmask 192.168.31.0/24
set address "Backup-Server-01" ip-netmask 192.168.50.10/32
set address "Monitoring-Host-01" ip-netmask 192.168.60.5/32
set address "Server-Web-01-Redundant" ip-netmask 192.168.10.10/32
set address "Server-DB-01-Redundant" ip-netmask 192.168.10.20/32
set address "Internal-Subnet-01-Redundant" ip-netmask 192.168.30.0/24
set address "DMZ-Host-01-Redundant" ip-netmask 172.16.10.5/32
set address "Workstation-01-Redundant" ip-netmask 192.168.20.10/32

set security rules "Allow-Web-Access" from trust to untrust source "Server-Web-01" destination any service service-http action allow
set security rules "Allow-DB-Access" from trust to dmz source "Server-DB-01" destination any service service-mysql action allow
set security rules "Workstation-Outbound" from trust to untrust source "Workstation-01" destination any service any action allow
set security rules "Workstation-Internal" from trust to trust source "Workstation-02" destination "Internal-Subnet-01" service any action allow
set security rules "DMZ-Web-Access" from dmz to untrust source "DMZ-Host-01" destination any service service-http action allow
set security rules "DMZ-Internal-Access" from dmz to trust source "DMZ-Host-02" destination "Internal-Subnet-02" service any action allow
set security rules "Guest-Internet" from guest to untrust source "Guest-Network" destination any service service-http action allow
set security rules "External-to-DMZ" from untrust to dmz source "External-Server-01" destination "DMZ-Host-01" service service-https action allow
set security rules "Internal-Communication" from trust to trust source "Internal-Subnet-01" destination "Internal-Subnet-02" service any action allow
set security rules "Deny-All" from any to any source any destination any service any action deny

set security rules "Allow-Web-Access-Redundant-1" from trust to untrust source "Server-Web-01" destination any service service-http action allow
set security rules "Allow-Web-Access-Redundant-2" from trust to untrust source "Server-Web-01" destination any service service-http action allow
set security rules "Allow-Web-Access-Redundant-3" from trust to untrust source "Server-Web-01" destination any service service-http action allow
set security rules "Allow-Web-Access-Redundant-4" from trust to untrust source "Server-Web-01" destination any service service-http action allow
set security rules "Allow-Web-Access-Redundant-5" from trust to untrust source "Server-Web-01" destination any service service-http action allow

set security rules "Allow-DB-Access-Duplicate-1" from trust to dmz source "Server-DB-01" destination any service service-mysql action allow
set security rules "Allow-DB-Access-Duplicate-2" from trust to dmz source "Server-DB-01" destination any service service-mysql action allow"""
    
    try:
        from src.utils.parse_config import parse_set_config
        
        print(f"📋 Testing with Expected Structure:")
        print(f"   Expected: 17 address objects, 17 security rules")
        
        rules_data, objects_data, metadata = parse_set_config(sample_content)
        
        print(f"\n📊 Parsing Results:")
        print(f"   Rules parsed: {len(rules_data)}")
        print(f"   Objects parsed: {len(objects_data)}")
        print(f"   Address objects: {metadata.get('address_object_count', 0)}")
        
        # Show sample objects
        if objects_data:
            print(f"\n📦 Sample Objects:")
            for i, obj in enumerate(objects_data[:5]):
                print(f"   {i+1}. {obj['name']} = {obj['value']}")
        
        # Check if this matches expectations
        expected_objects = 17
        expected_rules = 17
        
        print(f"\n🎯 Expected vs Actual:")
        print(f"   Objects: Expected={expected_objects}, Actual={len(objects_data)} {'✅' if len(objects_data) == expected_objects else '❌'}")
        print(f"   Rules: Expected={expected_rules}, Actual={len(rules_data)} {'✅' if len(rules_data) == expected_rules else '❌'}")
        
        if len(objects_data) == expected_objects and len(rules_data) == expected_rules:
            print(f"\n✅ Set parsing works correctly with proper format!")
            print(f"   The issue is with the actual file format, not the parser")
        else:
            print(f"\n❌ Set parsing has issues even with proper format")
        
        return True
        
    except Exception as e:
        print(f"❌ Set parsing test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DEBUGGING SET FILE STRUCTURE AND PARSING")
    print("=" * 70)
    
    # Debug the actual file structure
    content = debug_set_file_structure()
    
    # Test with known good format
    test_success = test_set_parsing_with_sample()
    
    print(f"\n📋 ANALYSIS SUMMARY:")
    if content:
        print(f"   ✅ File content retrieved and analyzed")
        print(f"   🔍 Check the command patterns above")
        print(f"   💡 The file format might be different than expected")
    else:
        print(f"   ❌ Could not retrieve file content")
    
    if test_success:
        print(f"   ✅ Set parser works with correct format")
        print(f"   🔧 Need to fix the actual file format or parser logic")
    else:
        print(f"   ❌ Set parser has fundamental issues")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Examine the actual file format structure")
    print(f"   2. Update set parser to handle the specific format")
    print(f"   3. Test with the corrected parser")
    print(f"   4. Verify object counts match expectations")
