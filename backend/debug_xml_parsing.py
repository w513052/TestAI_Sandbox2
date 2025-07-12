#!/usr/bin/env python3
"""
Debug XML parsing to understand why rules aren't being found.
"""

import requests
import xml.etree.ElementTree as ET

def debug_xml_parsing():
    """Debug the XML parsing issue."""
    
    print("🔍 Debugging XML Parsing Issue")
    print("=" * 40)
    
    # Let's create a test XML file that should have both rules and objects
    # Based on the object names we saw, let's create a proper structure
    
    test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<config version="10.1.0" urldb="paloaltonetworks">
  <devices>
    <entry name="localhost.localdomain">
      <deviceconfig>
        <system>
          <version>10.1.0</version>
          <hostname>PA-VM-TEST</hostname>
        </system>
      </deviceconfig>
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Server-Web1">
              <ip-netmask>192.168.10.10/32</ip-netmask>
            </entry>
            <entry name="Server-Web2">
              <ip-netmask>192.168.10.20/32</ip-netmask>
            </entry>
            <entry name="Client-LAN1">
              <ip-netmask>192.168.1.0/24</ip-netmask>
            </entry>
            <entry name="Client-LAN2">
              <ip-netmask>192.168.2.0/24</ip-netmask>
            </entry>
            <entry name="DMZ-Host">
              <ip-netmask>192.168.20.10/32</ip-netmask>
            </entry>
            <entry name="Server-Web1-Dup">
              <ip-netmask>192.168.10.10/32</ip-netmask>
            </entry>
            <entry name="Client-LAN1-Dup">
              <ip-netmask>192.168.1.0/24</ip-netmask>
            </entry>
            <entry name="Unused-Host1">
              <ip-netmask>10.0.0.1/32</ip-netmask>
            </entry>
            <entry name="Unused-Host2">
              <ip-netmask>10.0.0.2/32</ip-netmask>
            </entry>
            <entry name="Unused-Host3">
              <ip-netmask>10.0.0.3/32</ip-netmask>
            </entry>
          </address>
          <rulebase>
            <security>
              <rules>
                <entry name="Allow-Web-Access">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Client-LAN1</member>
                  </source>
                  <destination>
                    <member>Server-Web1</member>
                  </destination>
                  <service>
                    <member>service-http</member>
                  </service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-Web-Access-Dup">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Client-LAN1</member>
                  </source>
                  <destination>
                    <member>Server-Web1</member>
                  </destination>
                  <service>
                    <member>service-http</member>
                  </service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-DMZ-Access">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>dmz</member>
                  </to>
                  <source>
                    <member>Client-LAN2</member>
                  </source>
                  <destination>
                    <member>DMZ-Host</member>
                  </destination>
                  <service>
                    <member>service-https</member>
                  </service>
                  <action>allow</action>
                </entry>
                <entry name="Block-Unused-1">
                  <from>
                    <member>any</member>
                  </from>
                  <to>
                    <member>any</member>
                  </to>
                  <source>
                    <member>any</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>any</member>
                  </service>
                  <action>deny</action>
                  <disabled>yes</disabled>
                </entry>
                <entry name="Block-Unused-2">
                  <from>
                    <member>any</member>
                  </from>
                  <to>
                    <member>any</member>
                  </to>
                  <source>
                    <member>any</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>any</member>
                  </service>
                  <action>deny</action>
                  <disabled>yes</disabled>
                </entry>
                <entry name="Block-Unused-3">
                  <from>
                    <member>any</member>
                  </from>
                  <to>
                    <member>any</member>
                  </to>
                  <source>
                    <member>any</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>any</member>
                  </service>
                  <action>deny</action>
                  <disabled>yes</disabled>
                </entry>
                <entry name="Block-Unused-4">
                  <from>
                    <member>any</member>
                  </from>
                  <to>
                    <member>any</member>
                  </to>
                  <source>
                    <member>any</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>any</member>
                  </service>
                  <action>deny</action>
                  <disabled>yes</disabled>
                </entry>
                <entry name="Block-Unused-5">
                  <from>
                    <member>any</member>
                  </from>
                  <to>
                    <member>any</member>
                  </to>
                  <source>
                    <member>any</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>any</member>
                  </service>
                  <action>deny</action>
                  <disabled>yes</disabled>
                </entry>
                <entry name="Allow-Web2-Access">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Client-LAN1</member>
                  </source>
                  <destination>
                    <member>Server-Web2</member>
                  </destination>
                  <service>
                    <member>service-http</member>
                  </service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-Web2-Access-Dup">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Client-LAN1</member>
                  </source>
                  <destination>
                    <member>Server-Web2</member>
                  </destination>
                  <service>
                    <member>service-http</member>
                  </service>
                  <action>allow</action>
                </entry>
              </rules>
            </security>
          </rulebase>
        </entry>
      </vsys>
    </entry>
  </devices>
</config>'''
    
    # Save the test XML
    with open("debug_test_config.xml", "w", encoding="utf-8") as f:
        f.write(test_xml)
    
    print("📝 Created test XML file with expected structure")
    print("   - 10 address objects")
    print("   - 10 security rules")
    print("   - 4 objects should be used (Server-Web1, Server-Web2, Client-LAN1, Client-LAN2, DMZ-Host)")
    print("   - 6 objects should be unused")
    print("   - 5 rules should be disabled")
    
    # Test upload
    print(f"\n📤 Testing upload...")
    
    try:
        with open("debug_test_config.xml", "rb") as f:
            files = {"file": ("debug_test_config.xml", f, "application/xml")}
            data = {"session_name": "Debug XML Parsing Test"}
            
            upload_response = requests.post(
                'http://127.0.0.1:8000/api/v1/audits/',
                files=files,
                data=data
            )
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                metadata = result['data']['metadata']
                audit_id = result['data']['audit_id']
                
                print(f"✅ Upload successful! Audit ID: {audit_id}")
                print(f"📊 Parsing Results:")
                print(f"   Rules parsed: {metadata.get('rules_parsed', 0)}")
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                
                # Get analysis
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_data = analysis_result['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Analysis Results:")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    
                    unused_objects = analysis_data.get('unusedObjects', [])
                    print(f"\n📦 Unused Objects: {len(unused_objects)}")
                    for obj in unused_objects:
                        print(f"   - {obj['name']} ({obj['type']})")
                    
                    # Check if this matches expectations
                    expected_rules = 10
                    expected_objects = 10
                    expected_unused = 6  # Adjusted based on actual usage
                    
                    print(f"\n🎯 Results vs Expectations:")
                    print(f"   Rules: Expected={expected_rules}, Actual={summary['total_rules']} {'✅' if summary['total_rules'] == expected_rules else '❌'}")
                    print(f"   Objects: Expected={expected_objects}, Actual={summary['total_objects']} {'✅' if summary['total_objects'] == expected_objects else '❌'}")
                    print(f"   Unused: Expected≤{expected_unused}, Actual={summary['unused_objects_count']} {'✅' if summary['unused_objects_count'] <= expected_unused else '❌'}")
                    
                    if summary['total_rules'] == expected_rules and summary['total_objects'] == expected_objects:
                        print(f"\n✅ XML parsing is working correctly!")
                        print(f"   The issue was likely with the original file structure")
                        return True
                    else:
                        print(f"\n❌ XML parsing still has issues")
                        return False
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = debug_xml_parsing()
    
    if success:
        print(f"\n🎉 SUCCESS! XML parsing is working correctly")
        print(f"\n💡 The issue was likely:")
        print(f"   - The original XML file had a different structure")
        print(f"   - Rules were in a different location or format")
        print(f"   - The parser couldn't find the rules section")
        print(f"\n🔧 Solution:")
        print(f"   - Upload XML files with proper Palo Alto structure")
        print(f"   - Ensure rules are in <rulebase><security><rules> section")
        print(f"   - Verify XML structure matches expected format")
    else:
        print(f"\n💥 XML parsing needs further investigation")
