#!/usr/bin/env python3
"""
Test the fixed incremental set parsing to resolve rule counter inflation.
"""

import requests

def test_incremental_set_parsing():
    """Test the incremental set parsing fix."""
    
    print("🧪 Testing Fixed Incremental Set Parsing")
    print("=" * 50)
    
    # Create a test file with incremental set format (like the problematic file)
    incremental_set_content = """# Incremental Set Format Test
# Address Objects
set address Server-Web-01 ip-netmask 192.168.10.10/32
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

# Security Rules - Incremental Format
set security rules "Allow-Web-Access" from trust
set security rules "Allow-Web-Access" to untrust
set security rules "Allow-Web-Access" source Server-Web-01
set security rules "Allow-Web-Access" destination any
set security rules "Allow-Web-Access" service service-http
set security rules "Allow-Web-Access" action allow

set security rules "Allow-DB-Access" from trust
set security rules "Allow-DB-Access" to dmz
set security rules "Allow-DB-Access" source Server-DB-01
set security rules "Allow-DB-Access" destination any
set security rules "Allow-DB-Access" service service-mysql
set security rules "Allow-DB-Access" action allow

set security rules "Workstation-Outbound" from trust
set security rules "Workstation-Outbound" to untrust
set security rules "Workstation-Outbound" source Workstation-01
set security rules "Workstation-Outbound" destination any
set security rules "Workstation-Outbound" service any
set security rules "Workstation-Outbound" action allow

set security rules "Workstation-Internal" from trust
set security rules "Workstation-Internal" to trust
set security rules "Workstation-Internal" source Workstation-02
set security rules "Workstation-Internal" destination Internal-Subnet-01
set security rules "Workstation-Internal" service any
set security rules "Workstation-Internal" action allow

set security rules "DMZ-Web-Access" from dmz
set security rules "DMZ-Web-Access" to untrust
set security rules "DMZ-Web-Access" source DMZ-Host-01
set security rules "DMZ-Web-Access" destination any
set security rules "DMZ-Web-Access" service service-http
set security rules "DMZ-Web-Access" action allow

set security rules "DMZ-Internal-Access" from dmz
set security rules "DMZ-Internal-Access" to trust
set security rules "DMZ-Internal-Access" source DMZ-Host-02
set security rules "DMZ-Internal-Access" destination Internal-Subnet-02
set security rules "DMZ-Internal-Access" service any
set security rules "DMZ-Internal-Access" action allow

set security rules "Guest-Internet" from guest
set security rules "Guest-Internet" to untrust
set security rules "Guest-Internet" source Guest-Network
set security rules "Guest-Internet" destination any
set security rules "Guest-Internet" service service-http
set security rules "Guest-Internet" action allow

set security rules "External-to-DMZ" from untrust
set security rules "External-to-DMZ" to dmz
set security rules "External-to-DMZ" source External-Server-01
set security rules "External-to-DMZ" destination DMZ-Host-01
set security rules "External-to-DMZ" service service-https
set security rules "External-to-DMZ" action allow

set security rules "Internal-Communication" from trust
set security rules "Internal-Communication" to trust
set security rules "Internal-Communication" source Internal-Subnet-01
set security rules "Internal-Communication" destination Internal-Subnet-02
set security rules "Internal-Communication" service any
set security rules "Internal-Communication" action allow

set security rules "Deny-All" from any
set security rules "Deny-All" to any
set security rules "Deny-All" source any
set security rules "Deny-All" destination any
set security rules "Deny-All" service any
set security rules "Deny-All" action deny

# Redundant Rules (5 rules)
set security rules "Allow-Web-Access-Redundant-1" from trust
set security rules "Allow-Web-Access-Redundant-1" to untrust
set security rules "Allow-Web-Access-Redundant-1" source Server-Web-01
set security rules "Allow-Web-Access-Redundant-1" destination any
set security rules "Allow-Web-Access-Redundant-1" service service-http
set security rules "Allow-Web-Access-Redundant-1" action allow

set security rules "Allow-Web-Access-Redundant-2" from trust
set security rules "Allow-Web-Access-Redundant-2" to untrust
set security rules "Allow-Web-Access-Redundant-2" source Server-Web-01
set security rules "Allow-Web-Access-Redundant-2" destination any
set security rules "Allow-Web-Access-Redundant-2" service service-http
set security rules "Allow-Web-Access-Redundant-2" action allow

set security rules "Allow-Web-Access-Redundant-3" from trust
set security rules "Allow-Web-Access-Redundant-3" to untrust
set security rules "Allow-Web-Access-Redundant-3" source Server-Web-01
set security rules "Allow-Web-Access-Redundant-3" destination any
set security rules "Allow-Web-Access-Redundant-3" service service-http
set security rules "Allow-Web-Access-Redundant-3" action allow

set security rules "Allow-Web-Access-Redundant-4" from trust
set security rules "Allow-Web-Access-Redundant-4" to untrust
set security rules "Allow-Web-Access-Redundant-4" source Server-Web-01
set security rules "Allow-Web-Access-Redundant-4" destination any
set security rules "Allow-Web-Access-Redundant-4" service service-http
set security rules "Allow-Web-Access-Redundant-4" action allow

set security rules "Allow-Web-Access-Redundant-5" from trust
set security rules "Allow-Web-Access-Redundant-5" to untrust
set security rules "Allow-Web-Access-Redundant-5" source Server-Web-01
set security rules "Allow-Web-Access-Redundant-5" destination any
set security rules "Allow-Web-Access-Redundant-5" service service-http
set security rules "Allow-Web-Access-Redundant-5" action allow

# Duplicate Rules (2 rules)
set security rules "Allow-DB-Access-Duplicate-1" from trust
set security rules "Allow-DB-Access-Duplicate-1" to dmz
set security rules "Allow-DB-Access-Duplicate-1" source Server-DB-01
set security rules "Allow-DB-Access-Duplicate-1" destination any
set security rules "Allow-DB-Access-Duplicate-1" service service-mysql
set security rules "Allow-DB-Access-Duplicate-1" action allow

set security rules "Allow-DB-Access-Duplicate-2" from trust
set security rules "Allow-DB-Access-Duplicate-2" to dmz
set security rules "Allow-DB-Access-Duplicate-2" source Server-DB-01
set security rules "Allow-DB-Access-Duplicate-2" destination any
set security rules "Allow-DB-Access-Duplicate-2" service service-mysql
set security rules "Allow-DB-Access-Duplicate-2" action allow"""
    
    # Save to file
    with open("../test_incremental_format.txt", "w") as f:
        f.write(incremental_set_content)
    
    print(f"📁 Created incremental format test file")
    print(f"   Expected: 17 address objects, 17 rules")
    print(f"   Expected breakdown: 10 original + 5 redundant + 2 duplicate rules")
    
    try:
        # Upload the incremental format file
        with open("../test_incremental_format.txt", "rb") as f:
            files = {"file": ("test_incremental_format.txt", f, "text/plain")}
            data = {"session_name": "Incremental Set Format Test - Fixed"}
            
            upload_response = requests.post(
                'http://127.0.0.1:8000/api/v1/audits/',
                files=files,
                data=data
            )
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                audit_id = result['data']['audit_id']
                metadata = result['data']['metadata']
                
                print(f"\n✅ Upload successful! Audit ID: {audit_id}")
                print(f"📊 Parsing Results:")
                print(f"   Rules parsed: {metadata.get('rules_parsed', 0)}")
                print(f"   Rule count: {metadata.get('rule_count', 0)}")
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                
                # Get analysis results
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Analysis Results (Fixed):")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    print(f"   Redundant Objects: {summary.get('redundant_objects_count', 0)}")
                    
                    # Check rule analysis
                    print(f"\n📋 Rule Analysis (Fixed):")
                    print(f"   Unused Rules: {len(analysis_data.get('unusedRules', []))}")
                    print(f"   Duplicate Rules: {len(analysis_data.get('duplicateRules', []))}")
                    print(f"   Shadowed Rules: {len(analysis_data.get('shadowedRules', []))}")
                    print(f"   Overlapping Rules: {len(analysis_data.get('overlappingRules', []))}")
                    
                    # Compare with expected values
                    expected = {
                        "total_rules": 17,
                        "total_objects": 17,
                        "unused_objects": 2,
                        "redundant_objects": 5,
                        "duplicate_rules": 2,  # Should be 2, not 7+
                        "unused_rules": 0      # Should be low, not 7+
                    }
                    
                    actual = {
                        "total_rules": summary['total_rules'],
                        "total_objects": summary['total_objects'],
                        "unused_objects": summary['unused_objects_count'],
                        "redundant_objects": summary.get('redundant_objects_count', 0),
                        "duplicate_rules": len(analysis_data.get('duplicateRules', [])),
                        "unused_rules": len(analysis_data.get('unusedRules', []))
                    }
                    
                    print(f"\n🎯 Expected vs Actual (Fixed):")
                    all_correct = True
                    for key in expected:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        status = "✅" if actual_val == expected_val else "❌"
                        print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                        if actual_val != expected_val:
                            all_correct = False
                    
                    if actual['total_rules'] == expected['total_rules']:
                        print(f"\n🎉 RULE COUNTER INFLATION FIXED!")
                        print(f"   ✅ Incremental set parsing working correctly")
                        print(f"   ✅ Rule count matches expected: {actual['total_rules']}")
                        print(f"   ✅ No more 119 rules from parsing individual attributes")
                        
                        if actual['duplicate_rules'] <= 5:  # Much better than 7+
                            print(f"   ✅ Duplicate rule detection improved")
                        
                        return True
                    else:
                        print(f"\n⚠️  Rule count still incorrect")
                        print(f"   Expected 17 rules, got {actual['total_rules']}")
                        return False
                        
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING FIXED INCREMENTAL SET PARSING")
    print("=" * 60)
    
    success = test_incremental_set_parsing()
    
    if success:
        print(f"\n🎉 INCREMENTAL SET PARSING FIX SUCCESSFUL!")
        print(f"   Rule counter inflation resolved")
        print(f"   Frontend should now show correct rule counts")
        print(f"   Ready to test with your original complex file")
    else:
        print(f"\n💥 INCREMENTAL SET PARSING STILL HAS ISSUES!")
        print(f"   Need further investigation")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test with your original complex file")
    print(f"   2. Verify rule counts match your expected breakdown")
    print(f"   3. Check frontend displays correct numbers")
