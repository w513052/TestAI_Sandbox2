#!/usr/bin/env python3
"""
Simple test to debug parsing functions.
"""

from src.utils.parse_config import parse_rules, parse_objects, parse_metadata

def test_simple_parsing():
    """Test parsing with a very simple XML."""
    
    simple_xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <devices>
    <entry name="test">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Server-1">
              <ip-netmask>192.168.1.1/32</ip-netmask>
            </entry>
          </address>
          <rulebase>
            <security>
              <rules>
                <entry name="Test-Rule">
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

    print("Testing parse_rules...")
    try:
        rules = parse_rules(simple_xml)
        print(f"✅ Parsed {len(rules)} rules")
        if rules:
            print(f"   First rule: {rules[0]['rule_name']}")
    except Exception as e:
        print(f"❌ parse_rules failed: {str(e)}")
    
    print("\nTesting parse_objects...")
    try:
        objects = parse_objects(simple_xml)
        print(f"✅ Parsed {len(objects)} objects")
        if objects:
            print(f"   First object: {objects[0]['name']}")
    except Exception as e:
        print(f"❌ parse_objects failed: {str(e)}")
    
    print("\nTesting parse_metadata...")
    try:
        metadata = parse_metadata(simple_xml)
        print(f"✅ Parsed metadata with {len(metadata)} fields")
        print(f"   Metadata: {metadata}")
    except Exception as e:
        print(f"❌ parse_metadata failed: {str(e)}")

if __name__ == "__main__":
    test_simple_parsing()
