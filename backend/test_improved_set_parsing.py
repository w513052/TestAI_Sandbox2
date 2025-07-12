#!/usr/bin/env python3
"""
Test the improved set format parsing to handle various format variations.
"""

def test_preprocessing():
    """Test the preprocessing function with problematic content."""
    
    print("🧪 Testing Set Content Preprocessing")
    print("=" * 50)
    
    try:
        from src.utils.parse_config import preprocess_set_content
        
        # Test case 1: Concatenated commands (like what we saw in the debug)
        problematic_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32 set address Server-DB-01 ip-netmask 192.168.10.20/32 set address Workstation-01 ip-netmask 192.168.20.10/32
set security rules Allow-Web from trust to untrust source Server-Web-01 destination any service service-http action allow set security rules Allow-DB from trust to dmz source Server-DB-01 destination any service service-mysql action allow"""
        
        print(f"📋 Test Case 1: Concatenated Commands")
        print(f"   Original: {problematic_content[:100]}...")
        
        processed = preprocess_set_content(problematic_content)
        processed_lines = processed.split('\n')
        
        print(f"   Processed into {len(processed_lines)} lines:")
        for i, line in enumerate(processed_lines):
            print(f"   {i+1}. {line}")
        
        # Test case 2: Mixed format
        mixed_content = """set address "Server-1" ip-netmask 192.168.1.1/32
set address Server-2 ip-netmask 192.168.1.2/32 set address "Server-3" ip-netmask 192.168.1.3/32
set security rules "Rule-1" from trust to untrust source "Server-1" destination any service any action allow"""
        
        print(f"\n📋 Test Case 2: Mixed Format")
        processed2 = preprocess_set_content(mixed_content)
        processed2_lines = processed2.split('\n')
        
        print(f"   Processed into {len(processed2_lines)} lines:")
        for i, line in enumerate(processed2_lines):
            print(f"   {i+1}. {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Preprocessing test failed: {str(e)}")
        return False

def test_improved_parsing():
    """Test the improved parsing with various formats."""
    
    print(f"\n🧪 Testing Improved Set Parsing")
    print("=" * 50)
    
    try:
        from src.utils.parse_config import parse_set_config
        
        # Test with the expected 17 objects, 17 rules format
        test_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32
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
set security rules Allow-Web-Access from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-DB-Access from trust to dmz source Server-DB-01 destination any service service-mysql action allow
set security rules Workstation-Outbound from trust to untrust source Workstation-01 destination any service any action allow
set security rules Workstation-Internal from trust to trust source Workstation-02 destination Internal-Subnet-01 service any action allow
set security rules DMZ-Web-Access from dmz to untrust source DMZ-Host-01 destination any service service-http action allow
set security rules DMZ-Internal-Access from dmz to trust source DMZ-Host-02 destination Internal-Subnet-02 service any action allow
set security rules Guest-Internet from guest to untrust source Guest-Network destination any service service-http action allow
set security rules External-to-DMZ from untrust to dmz source External-Server-01 destination DMZ-Host-01 service service-https action allow
set security rules Internal-Communication from trust to trust source Internal-Subnet-01 destination Internal-Subnet-02 service any action allow
set security rules Deny-All from any to any source any destination any service any action deny
set security rules Allow-Web-Access-Redundant-1 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-2 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-3 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-4 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-5 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-DB-Access-Duplicate-1 from trust to dmz source Server-DB-01 destination any service service-mysql action allow
set security rules Allow-DB-Access-Duplicate-2 from trust to dmz source Server-DB-01 destination any service service-mysql action allow"""
        
        print(f"📋 Testing with Expected Structure:")
        print(f"   Expected: 17 address objects, 17 security rules")
        
        rules_data, objects_data, metadata = parse_set_config(test_content)
        
        print(f"\n📊 Parsing Results:")
        print(f"   Rules parsed: {len(rules_data)}")
        print(f"   Objects parsed: {len(objects_data)}")
        print(f"   Address objects: {metadata.get('address_object_count', 0)}")
        
        # Show sample objects to verify they're parsed correctly
        if objects_data:
            print(f"\n📦 Sample Objects:")
            for i, obj in enumerate(objects_data[:5]):
                print(f"   {i+1}. {obj['name']} = {obj['value']}")
        
        # Show sample rules to verify they're parsed correctly
        if rules_data:
            print(f"\n📋 Sample Rules:")
            for i, rule in enumerate(rules_data[:3]):
                print(f"   {i+1}. {rule['rule_name']}: {rule['src']} → {rule['dst']} | {rule['service']}")
        
        # Check if this matches expectations
        expected_objects = 17
        expected_rules = 17
        
        print(f"\n🎯 Expected vs Actual:")
        print(f"   Objects: Expected={expected_objects}, Actual={len(objects_data)} {'✅' if len(objects_data) == expected_objects else '❌'}")
        print(f"   Rules: Expected={expected_rules}, Actual={len(rules_data)} {'✅' if len(rules_data) == expected_rules else '❌'}")
        
        return len(objects_data) == expected_objects and len(rules_data) == expected_rules
        
    except Exception as e:
        print(f"❌ Improved parsing test failed: {str(e)}")
        return False

def test_with_upload():
    """Test by uploading a properly formatted file."""
    
    print(f"\n🧪 Testing with File Upload")
    print("=" * 50)
    
    # Create a test file with the expected structure
    test_file_content = """set address Server-Web-01 ip-netmask 192.168.10.10/32
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
set security rules Allow-Web-Access from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-DB-Access from trust to dmz source Server-DB-01 destination any service service-mysql action allow
set security rules Workstation-Outbound from trust to untrust source Workstation-01 destination any service any action allow
set security rules Workstation-Internal from trust to trust source Workstation-02 destination Internal-Subnet-01 service any action allow
set security rules DMZ-Web-Access from dmz to untrust source DMZ-Host-01 destination any service service-http action allow
set security rules DMZ-Internal-Access from dmz to trust source DMZ-Host-02 destination Internal-Subnet-02 service any action allow
set security rules Guest-Internet from guest to untrust source Guest-Network destination any service service-http action allow
set security rules External-to-DMZ from untrust to dmz source External-Server-01 destination DMZ-Host-01 service service-https action allow
set security rules Internal-Communication from trust to trust source Internal-Subnet-01 destination Internal-Subnet-02 service any action allow
set security rules Deny-All from any to any source any destination any service any action deny
set security rules Allow-Web-Access-Redundant-1 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-2 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-3 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-4 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-Web-Access-Redundant-5 from trust to untrust source Server-Web-01 destination any service service-http action allow
set security rules Allow-DB-Access-Duplicate-1 from trust to dmz source Server-DB-01 destination any service service-mysql action allow
set security rules Allow-DB-Access-Duplicate-2 from trust to dmz source Server-DB-01 destination any service service-mysql action allow"""
    
    # Save to file
    with open("../test_expected_format.txt", "w") as f:
        f.write(test_file_content)
    
    print(f"📁 Created test file: test_expected_format.txt")
    print(f"   Expected: 17 address objects, 17 rules")
    print(f"   Expected unused: 2 objects (Backup-Server-01, Monitoring-Host-01)")
    
    try:
        import requests
        
        # Upload the file
        with open("../test_expected_format.txt", "rb") as f:
            files = {"file": ("test_expected_format.txt", f, "text/plain")}
            data = {"session_name": "Test Expected Format - Improved Parser"}
            
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
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                
                # Get analysis
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
                    
                    # Check against expectations
                    expected = {
                        "total_objects": 17,
                        "total_rules": 17,
                        "unused_objects": 2,  # Backup-Server-01, Monitoring-Host-01
                        "redundant_objects": 5  # 5 redundant objects
                    }
                    
                    actual = {
                        "total_objects": summary['total_objects'],
                        "total_rules": summary['total_rules'],
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
                    
                    return all_correct
                    
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Upload test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING IMPROVED SET FORMAT PARSING")
    print("=" * 70)
    
    # Test preprocessing
    preprocess_success = test_preprocessing()
    
    # Test improved parsing
    parsing_success = test_improved_parsing()
    
    # Test with upload
    upload_success = test_with_upload()
    
    print(f"\n📋 FINAL RESULTS:")
    print(f"   Preprocessing: {'✅ PASS' if preprocess_success else '❌ FAIL'}")
    print(f"   Improved Parsing: {'✅ PASS' if parsing_success else '❌ FAIL'}")
    print(f"   Upload Test: {'✅ PASS' if upload_success else '❌ FAIL'}")
    
    if preprocess_success and parsing_success and upload_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Improved set format parsing is working correctly")
        print(f"   Should now handle the complex file format properly")
        print(f"   Ready to test with your original file")
    else:
        print(f"\n💥 SOME TESTS FAILED!")
        print(f"   Need further improvements to handle the file format")
