#!/usr/bin/env python3
"""
Simple test to debug XML upload issue.
"""

import requests

def test_xml_upload():
    xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
<config version="10.1.0">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Server-001">
              <ip-netmask>192.168.1.10/32</ip-netmask>
            </entry>
          </address>
          <rulebase>
            <security>
              <rules>
                <entry name="Allow-Web-Traffic">
                  <from><member>trust</member></from>
                  <to><member>untrust</member></to>
                  <source><member>any</member></source>
                  <destination><member>any</member></destination>
                  <service><member>any</member></service>
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

    files = {
        'file': ('test.xml', xml_content, 'application/xml')
    }
    data = {
        'session_name': 'Simple_XML_Test'
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/audits/',
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            import json
            data = response.json()
            print(f"Success! Audit ID: {data['data']['audit_id']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_xml_upload()
