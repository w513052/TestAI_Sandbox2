#!/usr/bin/env python3
"""
Unit tests for parsing across different Palo Alto firmware versions.
Task 18: Validate Parsing Across Firmware Versions
"""

import pytest
import logging
from src.utils.parse_config import parse_rules, parse_objects, parse_metadata

# Configure logging for test traceability and debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_panos_9x_config():
    """Create a sample PAN-OS 9.x configuration for testing."""
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<config version="9.1.0">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Web-Server-9x">
              <ip-netmask>192.168.1.10/32</ip-netmask>
              <description>Web server for 9.x firmware</description>
            </entry>
            <entry name="Database-Server-9x">
              <ip-netmask>192.168.2.10/32</ip-netmask>
              <tag>
                <member>production</member>
                <member>database</member>
              </tag>
            </entry>
            <entry name="App-Server-9x">
              <fqdn>app.example.com</fqdn>
              <description>Application server</description>
            </entry>
          </address>
          <service>
            <entry name="HTTP-Service-9x">
              <protocol>
                <tcp>
                  <port>80</port>
                </tcp>
              </protocol>
              <description>HTTP service for 9.x</description>
            </entry>
            <entry name="HTTPS-Service-9x">
              <protocol>
                <tcp>
                  <port>443</port>
                </tcp>
              </protocol>
              <tag>
                <member>web-services</member>
              </tag>
            </entry>
            <entry name="Custom-Service-9x">
              <protocol>
                <tcp>
                  <port>8080-8090</port>
                </tcp>
              </protocol>
            </entry>
          </service>
          <rulebase>
            <security>
              <rules>
                <entry name="Allow-Web-9x">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Web-Server-9x</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>HTTP-Service-9x</member>
                  </service>
                  <action>allow</action>
                  <description>Allow web traffic in 9.x</description>
                </entry>
                <entry name="Allow-HTTPS-9x">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Web-Server-9x</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>HTTPS-Service-9x</member>
                  </service>
                  <action>allow</action>
                  <log-setting>default</log-setting>
                </entry>
                <entry name="Allow-Database-9x">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>dmz</member>
                  </to>
                  <source>
                    <member>App-Server-9x</member>
                  </source>
                  <destination>
                    <member>Database-Server-9x</member>
                  </destination>
                  <service>
                    <member>any</member>
                  </service>
                  <action>allow</action>
                  <disabled>no</disabled>
                </entry>
              </rules>
            </security>
          </rulebase>
        </entry>
      </vsys>
    </entry>
  </devices>
</config>'''

def create_panos_10x_config():
    """Create a sample PAN-OS 10.x configuration for testing."""
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<config version="10.2.0">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Web-Server-10x">
              <ip-netmask>192.168.1.20/32</ip-netmask>
              <description>Web server for 10.x firmware</description>
              <tag>
                <member>web-tier</member>
                <member>production</member>
              </tag>
            </entry>
            <entry name="Database-Server-10x">
              <ip-netmask>192.168.2.20/32</ip-netmask>
              <description>Database server with enhanced attributes</description>
            </entry>
            <entry name="App-Server-10x">
              <ip-range>192.168.3.10-192.168.3.20</ip-range>
              <description>Application server range</description>
            </entry>
            <entry name="Cloud-Server-10x">
              <fqdn>cloud.example.com</fqdn>
              <tag>
                <member>cloud</member>
                <member>external</member>
              </tag>
            </entry>
          </address>
          <service>
            <entry name="HTTP-Service-10x">
              <protocol>
                <tcp>
                  <port>80</port>
                </tcp>
              </protocol>
              <description>Enhanced HTTP service for 10.x</description>
              <tag>
                <member>web-services</member>
              </tag>
            </entry>
            <entry name="HTTPS-Service-10x">
              <protocol>
                <tcp>
                  <port>443</port>
                </tcp>
              </protocol>
              <description>HTTPS with enhanced security</description>
            </entry>
            <entry name="Multi-Port-Service-10x">
              <protocol>
                <tcp>
                  <port>8080,8443,9090</port>
                </tcp>
              </protocol>
              <description>Multiple port service</description>
            </entry>
          </service>
          <rulebase>
            <security>
              <rules>
                <entry name="Allow-Web-10x" uuid="12345678-1234-5678-9abc-123456789012">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Web-Server-10x</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>HTTP-Service-10x</member>
                  </service>
                  <action>allow</action>
                  <description>Allow web traffic in 10.x with UUID</description>
                  <log-setting>enhanced-logging</log-setting>
                  <profile-setting>
                    <profiles>
                      <virus>
                        <member>default</member>
                      </virus>
                    </profiles>
                  </profile-setting>
                </entry>
                <entry name="Allow-HTTPS-10x" uuid="87654321-4321-8765-cba9-987654321098">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Web-Server-10x</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>HTTPS-Service-10x</member>
                  </service>
                  <action>allow</action>
                  <description>HTTPS with enhanced features</description>
                  <disabled>no</disabled>
                </entry>
                <entry name="Allow-Cloud-Access-10x" uuid="11111111-2222-3333-4444-555555555555">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>App-Server-10x</member>
                  </source>
                  <destination>
                    <member>Cloud-Server-10x</member>
                  </destination>
                  <service>
                    <member>Multi-Port-Service-10x</member>
                  </service>
                  <action>allow</action>
                  <description>Cloud access rule with new features</description>
                  <log-start>yes</log-start>
                  <log-end>yes</log-end>
                </entry>
              </rules>
            </security>
          </rulebase>
        </entry>
      </vsys>
    </entry>
  </devices>
</config>'''

def create_panos_11x_config():
    """Create a sample PAN-OS 11.x configuration for testing (future version)."""
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<config version="11.0.0">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Modern-Server-11x">
              <ip-netmask>192.168.1.30/32</ip-netmask>
              <description>Modern server for 11.x firmware</description>
              <tag>
                <member>modern</member>
                <member>high-security</member>
              </tag>
            </entry>
            <entry name="Container-Network-11x">
              <ip-netmask>10.0.0.0/16</ip-netmask>
              <description>Container network range</description>
            </entry>
          </address>
          <service>
            <entry name="Modern-HTTP-11x">
              <protocol>
                <tcp>
                  <port>80</port>
                </tcp>
              </protocol>
              <description>Modern HTTP service</description>
            </entry>
          </service>
          <rulebase>
            <security>
              <rules>
                <entry name="Modern-Rule-11x" uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee">
                  <from>
                    <member>trust</member>
                  </from>
                  <to>
                    <member>untrust</member>
                  </to>
                  <source>
                    <member>Modern-Server-11x</member>
                  </source>
                  <destination>
                    <member>any</member>
                  </destination>
                  <service>
                    <member>Modern-HTTP-11x</member>
                  </service>
                  <action>allow</action>
                  <description>Modern rule with future features</description>
                  <log-setting>modern-logging</log-setting>
                  <disabled>no</disabled>
                </entry>
              </rules>
            </security>
          </rulebase>
        </entry>
      </vsys>
    </entry>
  </devices>
</config>'''

class TestFirmwareVersionParsing:
    """Test cases for parsing across different firmware versions."""

    def test_panos_9x_parsing(self):
        """Test parsing of PAN-OS 9.x configuration."""
        logger.info("Testing PAN-OS 9.x configuration parsing")
        
        config_9x = create_panos_9x_config()
        
        # Parse all components
        rules_9x = parse_rules(config_9x)
        objects_9x = parse_objects(config_9x)
        metadata_9x = parse_metadata(config_9x)
        
        logger.info(f"9.x parsing results: {len(rules_9x)} rules, {len(objects_9x)} objects")
        
        # Verify parsing results
        assert len(rules_9x) >= 3, f"Expected at least 3 rules from 9.x config, got {len(rules_9x)}"
        assert len(objects_9x) >= 6, f"Expected at least 6 objects from 9.x config, got {len(objects_9x)}"
        
        # Verify rule attributes specific to 9.x
        rule_names_9x = [rule["rule_name"] for rule in rules_9x]
        assert "Allow-Web-9x" in rule_names_9x, "Should contain 9.x specific rule"
        assert "Allow-HTTPS-9x" in rule_names_9x, "Should contain 9.x HTTPS rule"
        assert "Allow-Database-9x" in rule_names_9x, "Should contain 9.x database rule"
        
        # Verify object attributes
        object_names_9x = [obj["name"] for obj in objects_9x]
        assert "Web-Server-9x" in object_names_9x, "Should contain 9.x web server object"
        assert "HTTP-Service-9x" in object_names_9x, "Should contain 9.x HTTP service"
        
        # Verify metadata contains firmware version
        assert "firmware_version" in metadata_9x, "Metadata should contain firmware version"
        
        logger.info("PAN-OS 9.x parsing test completed successfully")
        return rules_9x, objects_9x, metadata_9x

    def test_panos_10x_parsing(self):
        """Test parsing of PAN-OS 10.x configuration."""
        logger.info("Testing PAN-OS 10.x configuration parsing")
        
        config_10x = create_panos_10x_config()
        
        # Parse all components
        rules_10x = parse_rules(config_10x)
        objects_10x = parse_objects(config_10x)
        metadata_10x = parse_metadata(config_10x)
        
        logger.info(f"10.x parsing results: {len(rules_10x)} rules, {len(objects_10x)} objects")
        
        # Verify parsing results
        assert len(rules_10x) >= 3, f"Expected at least 3 rules from 10.x config, got {len(rules_10x)}"
        assert len(objects_10x) >= 7, f"Expected at least 7 objects from 10.x config, got {len(objects_10x)}"
        
        # Verify rule attributes specific to 10.x
        rule_names_10x = [rule["rule_name"] for rule in rules_10x]
        assert "Allow-Web-10x" in rule_names_10x, "Should contain 10.x specific rule"
        assert "Allow-HTTPS-10x" in rule_names_10x, "Should contain 10.x HTTPS rule"
        assert "Allow-Cloud-Access-10x" in rule_names_10x, "Should contain 10.x cloud rule"
        
        # Verify object attributes
        object_names_10x = [obj["name"] for obj in objects_10x]
        assert "Web-Server-10x" in object_names_10x, "Should contain 10.x web server object"
        assert "Cloud-Server-10x" in object_names_10x, "Should contain 10.x cloud server object"
        assert "Multi-Port-Service-10x" in object_names_10x, "Should contain 10.x multi-port service"
        
        # Verify metadata contains firmware version
        assert "firmware_version" in metadata_10x, "Metadata should contain firmware version"
        
        logger.info("PAN-OS 10.x parsing test completed successfully")
        return rules_10x, objects_10x, metadata_10x

    def test_panos_11x_parsing(self):
        """Test parsing of PAN-OS 11.x configuration (future version)."""
        logger.info("Testing PAN-OS 11.x configuration parsing")
        
        config_11x = create_panos_11x_config()
        
        # Parse all components
        rules_11x = parse_rules(config_11x)
        objects_11x = parse_objects(config_11x)
        metadata_11x = parse_metadata(config_11x)
        
        logger.info(f"11.x parsing results: {len(rules_11x)} rules, {len(objects_11x)} objects")
        
        # Verify parsing results
        assert len(rules_11x) >= 1, f"Expected at least 1 rule from 11.x config, got {len(rules_11x)}"
        assert len(objects_11x) >= 3, f"Expected at least 3 objects from 11.x config, got {len(objects_11x)}"
        
        # Verify rule attributes specific to 11.x
        rule_names_11x = [rule["rule_name"] for rule in rules_11x]
        assert "Modern-Rule-11x" in rule_names_11x, "Should contain 11.x specific rule"
        
        # Verify object attributes
        object_names_11x = [obj["name"] for obj in objects_11x]
        assert "Modern-Server-11x" in object_names_11x, "Should contain 11.x modern server object"
        assert "Container-Network-11x" in object_names_11x, "Should contain 11.x container network"
        
        logger.info("PAN-OS 11.x parsing test completed successfully")
        return rules_11x, objects_11x, metadata_11x

    def test_cross_version_consistency(self):
        """Test that rule and object attributes are correctly extracted across firmware versions."""
        logger.info("Testing cross-version parsing consistency")

        # Parse all versions
        rules_9x, objects_9x, metadata_9x = self.test_panos_9x_parsing()
        rules_10x, objects_10x, metadata_10x = self.test_panos_10x_parsing()
        rules_11x, objects_11x, metadata_11x = self.test_panos_11x_parsing()

        # Verify consistent rule structure across versions
        all_rules = [rules_9x, rules_10x, rules_11x]
        version_names = ["9.x", "10.x", "11.x"]

        for i, (rules, version) in enumerate(zip(all_rules, version_names)):
            logger.info(f"Validating {version} rule structure consistency")

            for rule in rules:
                # Check that all versions have the same required fields
                required_fields = ["rule_name", "rule_type", "src_zone", "dst_zone",
                                 "src", "dst", "service", "action", "position", "is_disabled"]

                for field in required_fields:
                    assert field in rule, f"{version} rule missing required field: {field}"

                # Verify field types are consistent
                assert isinstance(rule["rule_name"], str), f"{version} rule_name should be string"
                assert isinstance(rule["position"], int), f"{version} position should be integer"
                assert isinstance(rule["is_disabled"], bool), f"{version} is_disabled should be boolean"
                assert rule["action"] in ["allow", "deny", "drop"], f"{version} invalid action: {rule['action']}"

        # Verify consistent object structure across versions
        all_objects = [objects_9x, objects_10x, objects_11x]

        for i, (objects, version) in enumerate(zip(all_objects, version_names)):
            logger.info(f"Validating {version} object structure consistency")

            for obj in objects:
                # Check that all versions have the same required fields
                required_fields = ["name", "object_type", "value"]

                for field in required_fields:
                    assert field in obj, f"{version} object missing required field: {field}"

                # Verify field types are consistent
                assert isinstance(obj["name"], str), f"{version} object name should be string"
                assert isinstance(obj["object_type"], str), f"{version} object_type should be string"
                assert obj["object_type"] in ["address", "service"], f"{version} invalid object_type: {obj['object_type']}"

        # Log any parsing inconsistencies for debugging
        inconsistencies = []

        # Check for different field availability across versions
        all_rule_fields = set()
        for rules in all_rules:
            for rule in rules:
                all_rule_fields.update(rule.keys())

        for i, (rules, version) in enumerate(zip(all_rules, version_names)):
            for rule in rules:
                missing_fields = all_rule_fields - set(rule.keys())
                if missing_fields:
                    inconsistency = f"{version} rule '{rule['rule_name']}' missing fields: {missing_fields}"
                    inconsistencies.append(inconsistency)
                    logger.warning(inconsistency)

        all_object_fields = set()
        for objects in all_objects:
            for obj in objects:
                all_object_fields.update(obj.keys())

        for i, (objects, version) in enumerate(zip(all_objects, version_names)):
            for obj in objects:
                missing_fields = all_object_fields - set(obj.keys())
                if missing_fields:
                    inconsistency = f"{version} object '{obj['name']}' missing fields: {missing_fields}"
                    inconsistencies.append(inconsistency)
                    logger.warning(inconsistency)

        # Log summary of inconsistencies
        if inconsistencies:
            logger.warning(f"Found {len(inconsistencies)} parsing inconsistencies across firmware versions")
            for inconsistency in inconsistencies[:10]:  # Log first 10 for brevity
                logger.warning(f"  - {inconsistency}")
        else:
            logger.info("No parsing inconsistencies found across firmware versions")

        logger.info("Cross-version consistency test completed successfully")

    def test_firmware_specific_attributes(self):
        """Test that firmware-specific attributes are handled correctly."""
        logger.info("Testing firmware-specific attribute handling")

        # Test 9.x specific features
        config_9x = create_panos_9x_config()
        rules_9x = parse_rules(config_9x)

        # 9.x should handle basic attributes
        for rule in rules_9x:
            if rule["rule_name"] == "Allow-Web-9x":
                # Should have basic required fields
                assert rule["src_zone"] == "trust", "9.x should parse src_zone correctly"
                assert rule["dst_zone"] == "untrust", "9.x should parse dst_zone correctly"
                assert rule["action"] == "allow", "9.x should parse action correctly"

        # Test 10.x specific features
        config_10x = create_panos_10x_config()
        rules_10x = parse_rules(config_10x)

        # 10.x should handle enhanced attributes
        for rule in rules_10x:
            if rule["rule_name"] == "Allow-Web-10x":
                # Should have all basic fields plus potentially enhanced ones
                assert rule["src_zone"] == "trust", "10.x should parse src_zone correctly"
                assert rule["dst_zone"] == "untrust", "10.x should parse dst_zone correctly"
                assert rule["action"] == "allow", "10.x should parse action correctly"

        # Test object parsing across versions
        objects_9x = parse_objects(config_9x)
        objects_10x = parse_objects(config_10x)

        # Both versions should parse address objects correctly
        address_9x = [obj for obj in objects_9x if obj["object_type"] == "address"]
        address_10x = [obj for obj in objects_10x if obj["object_type"] == "address"]

        assert len(address_9x) >= 3, "9.x should parse address objects"
        assert len(address_10x) >= 4, "10.x should parse address objects"

        # Both versions should parse service objects correctly
        service_9x = [obj for obj in objects_9x if obj["object_type"] == "service"]
        service_10x = [obj for obj in objects_10x if obj["object_type"] == "service"]

        assert len(service_9x) >= 3, "9.x should parse service objects"
        assert len(service_10x) >= 3, "10.x should parse service objects"

        logger.info("Firmware-specific attribute handling test completed successfully")

    def test_metadata_extraction_across_versions(self):
        """Test metadata extraction consistency across firmware versions."""
        logger.info("Testing metadata extraction across firmware versions")

        # Parse metadata from all versions
        config_9x = create_panos_9x_config()
        config_10x = create_panos_10x_config()
        config_11x = create_panos_11x_config()

        metadata_9x = parse_metadata(config_9x)
        metadata_10x = parse_metadata(config_10x)
        metadata_11x = parse_metadata(config_11x)

        # All versions should have consistent metadata structure
        all_metadata = [metadata_9x, metadata_10x, metadata_11x]
        version_names = ["9.x", "10.x", "11.x"]

        for metadata, version in zip(all_metadata, version_names):
            logger.info(f"Validating {version} metadata: {metadata}")

            # Check required metadata fields
            required_fields = ["rule_count", "address_object_count", "service_object_count"]

            for field in required_fields:
                assert field in metadata, f"{version} metadata missing field: {field}"
                assert isinstance(metadata[field], int), f"{version} {field} should be integer"
                assert metadata[field] >= 0, f"{version} {field} should be non-negative"

        # Verify rule counts match actual parsed rules
        rules_9x = parse_rules(config_9x)
        rules_10x = parse_rules(config_10x)
        rules_11x = parse_rules(config_11x)

        assert metadata_9x["rule_count"] == len(rules_9x), "9.x metadata rule count should match parsed rules"
        assert metadata_10x["rule_count"] == len(rules_10x), "10.x metadata rule count should match parsed rules"
        assert metadata_11x["rule_count"] == len(rules_11x), "11.x metadata rule count should match parsed rules"

        logger.info("Metadata extraction consistency test completed successfully")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
