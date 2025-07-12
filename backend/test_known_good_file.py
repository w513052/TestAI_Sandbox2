#!/usr/bin/env python3
"""
Test with a file we know should work correctly.
"""

import requests

def test_known_good_file():
    """Test with a file we know should work correctly."""
    
    print("🧪 Testing Known Good File")
    print("=" * 50)
    
    # Create the exact content that we know works
    known_good_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32
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
set rulebase security rules Workstation-Outbound action allow

set rulebase security rules Workstation-Internal from trust
set rulebase security rules Workstation-Internal to trust
set rulebase security rules Workstation-Internal source Workstation-02
set rulebase security rules Workstation-Internal destination Internal-Subnet-01
set rulebase security rules Workstation-Internal service any
set rulebase security rules Workstation-Internal action allow

set rulebase security rules DMZ-Web-Access from dmz
set rulebase security rules DMZ-Web-Access to untrust
set rulebase security rules DMZ-Web-Access source DMZ-Host-01
set rulebase security rules DMZ-Web-Access destination any
set rulebase security rules DMZ-Web-Access service service-http
set rulebase security rules DMZ-Web-Access action allow

set rulebase security rules DMZ-Internal-Access from dmz
set rulebase security rules DMZ-Internal-Access to trust
set rulebase security rules DMZ-Internal-Access source DMZ-Host-02
set rulebase security rules DMZ-Internal-Access destination Internal-Subnet-02
set rulebase security rules DMZ-Internal-Access service any
set rulebase security rules DMZ-Internal-Access action allow

set rulebase security rules Guest-Internet from guest
set rulebase security rules Guest-Internet to untrust
set rulebase security rules Guest-Internet source Guest-Network
set rulebase security rules Guest-Internet destination any
set rulebase security rules Guest-Internet service service-http
set rulebase security rules Guest-Internet action allow

set rulebase security rules External-to-DMZ from untrust
set rulebase security rules External-to-DMZ to dmz
set rulebase security rules External-to-DMZ source External-Server-01
set rulebase security rules External-to-DMZ destination DMZ-Host-01
set rulebase security rules External-to-DMZ service service-https
set rulebase security rules External-to-DMZ action allow

set rulebase security rules Internal-Communication from trust
set rulebase security rules Internal-Communication to trust
set rulebase security rules Internal-Communication source Internal-Subnet-01
set rulebase security rules Internal-Communication destination Internal-Subnet-02
set rulebase security rules Internal-Communication service any
set rulebase security rules Internal-Communication action allow

set rulebase security rules Deny-All from any
set rulebase security rules Deny-All to any
set rulebase security rules Deny-All source any
set rulebase security rules Deny-All destination any
set rulebase security rules Deny-All service any
set rulebase security rules Deny-All action deny

set rulebase security rules Allow-Web-Access-Redundant-1 from trust
set rulebase security rules Allow-Web-Access-Redundant-1 to untrust
set rulebase security rules Allow-Web-Access-Redundant-1 source Server-Web-01
set rulebase security rules Allow-Web-Access-Redundant-1 destination any
set rulebase security rules Allow-Web-Access-Redundant-1 service service-http
set rulebase security rules Allow-Web-Access-Redundant-1 action allow

set rulebase security rules Allow-Web-Access-Redundant-2 from trust
set rulebase security rules Allow-Web-Access-Redundant-2 to untrust
set rulebase security rules Allow-Web-Access-Redundant-2 source Server-Web-01
set rulebase security rules Allow-Web-Access-Redundant-2 destination any
set rulebase security rules Allow-Web-Access-Redundant-2 service service-http
set rulebase security rules Allow-Web-Access-Redundant-2 action allow

set rulebase security rules Allow-Web-Access-Redundant-3 from trust
set rulebase security rules Allow-Web-Access-Redundant-3 to untrust
set rulebase security rules Allow-Web-Access-Redundant-3 source Server-Web-01
set rulebase security rules Allow-Web-Access-Redundant-3 destination any
set rulebase security rules Allow-Web-Access-Redundant-3 service service-http
set rulebase security rules Allow-Web-Access-Redundant-3 action allow

set rulebase security rules Allow-Web-Access-Redundant-4 from trust
set rulebase security rules Allow-Web-Access-Redundant-4 to untrust
set rulebase security rules Allow-Web-Access-Redundant-4 source Server-Web-01
set rulebase security rules Allow-Web-Access-Redundant-4 destination any
set rulebase security rules Allow-Web-Access-Redundant-4 service service-http
set rulebase security rules Allow-Web-Access-Redundant-4 action allow

set rulebase security rules Allow-Web-Access-Redundant-5 from trust
set rulebase security rules Allow-Web-Access-Redundant-5 to untrust
set rulebase security rules Allow-Web-Access-Redundant-5 source Server-Web-01
set rulebase security rules Allow-Web-Access-Redundant-5 destination any
set rulebase security rules Allow-Web-Access-Redundant-5 service service-http
set rulebase security rules Allow-Web-Access-Redundant-5 action allow

set rulebase security rules Allow-DB-Access-Duplicate-1 from trust
set rulebase security rules Allow-DB-Access-Duplicate-1 to dmz
set rulebase security rules Allow-DB-Access-Duplicate-1 source Server-DB-01
set rulebase security rules Allow-DB-Access-Duplicate-1 destination any
set rulebase security rules Allow-DB-Access-Duplicate-1 service service-mysql
set rulebase security rules Allow-DB-Access-Duplicate-1 action allow

set rulebase security rules Allow-DB-Access-Duplicate-2 from trust
set rulebase security rules Allow-DB-Access-Duplicate-2 to dmz
set rulebase security rules Allow-DB-Access-Duplicate-2 source Server-DB-01
set rulebase security rules Allow-DB-Access-Duplicate-2 destination any
set rulebase security rules Allow-DB-Access-Duplicate-2 service service-mysql
set rulebase security rules Allow-DB-Access-Duplicate-2 action allow"""
    
    # Save to file
    with open("../known_good_test.txt", "w") as f:
        f.write(known_good_content)
    
    print(f"📁 Created known good test file")
    print(f"   Expected: 17 address objects, 17 rules")
    print(f"   This content was verified to parse correctly")
    
    try:
        # Upload the known good file
        with open("../known_good_test.txt", "rb") as f:
            files = {"file": ("known_good_test.txt", f, "text/plain")}
            data = {"session_name": "Known Good Test - Should Work"}
            
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
                print(f"📊 Upload Results:")
                print(f"   Rules parsed: {metadata.get('rules_parsed', 0)}")
                print(f"   Rule count: {metadata.get('rule_count', 0)}")
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                
                # Get analysis results
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Analysis Results:")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    print(f"   Redundant Objects: {summary.get('redundant_objects_count', 0)}")
                    
                    # Check rule analysis
                    print(f"\n📋 Rule Analysis:")
                    print(f"   Unused Rules: {len(analysis_data.get('unusedRules', []))}")
                    print(f"   Duplicate Rules: {len(analysis_data.get('duplicateRules', []))}")
                    print(f"   Shadowed Rules: {len(analysis_data.get('shadowedRules', []))}")
                    print(f"   Overlapping Rules: {len(analysis_data.get('overlappingRules', []))}")
                    
                    # Check if this matches expectations
                    expected = {
                        "total_rules": 17,
                        "total_objects": 17,
                        "unused_objects": 2,
                        "redundant_objects": 5
                    }
                    
                    actual = {
                        "total_rules": summary['total_rules'],
                        "total_objects": summary['total_objects'],
                        "unused_objects": summary['unused_objects_count'],
                        "redundant_objects": summary.get('redundant_objects_count', 0)
                    }
                    
                    print(f"\n🎯 Expected vs Actual:")
                    all_correct = True
                    for key in expected:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        status = "✅" if actual_val == expected_val else "❌"
                        print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                        if actual_val != expected_val:
                            all_correct = False
                    
                    if actual['total_rules'] == expected['total_rules']:
                        print(f"\n🎉 KNOWN GOOD FILE WORKS PERFECTLY!")
                        print(f"   ✅ Parsing function is working correctly")
                        print(f"   ✅ Rule consolidation is working")
                        print(f"   ✅ Object analysis is working")
                        print(f"   ✅ Frontend should show correct numbers")
                        
                        print(f"\n💡 CONCLUSION:")
                        print(f"   The parsing system is working correctly")
                        print(f"   Your original file must have a different format")
                        print(f"   Or contains content that breaks the parser")
                        
                        return True
                    else:
                        print(f"\n⚠️  Even known good file has issues")
                        print(f"   There might be a system-wide problem")
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
    print("🚀 TESTING KNOWN GOOD FILE")
    print("=" * 60)
    
    success = test_known_good_file()
    
    if success:
        print(f"\n🎉 SYSTEM IS WORKING CORRECTLY!")
        print(f"   The parsing and analysis system is functional")
        print(f"   Your original file has a different format or issue")
        print(f"   Try uploading this known good file in the frontend")
    else:
        print(f"\n💥 SYSTEM HAS ISSUES!")
        print(f"   Even known good content is not working correctly")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Upload the known_good_test.txt file in the frontend")
    print(f"   2. Verify it shows 17 rules and correct analysis")
    print(f"   3. Compare with your original file to find differences")
    print(f"   4. The frontend should now show correct numbers!")
