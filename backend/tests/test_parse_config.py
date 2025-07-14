#!/usr/bin/env python3
"""
Unit tests for XML and SET parsing functions.
Task 15: Write Unit Tests for XML Parsing
Task 16: Write Unit Tests for Set-Format Parsing
"""

import pytest
import logging
from src.utils.parse_config import parse_rules, parse_objects, parse_metadata, parse_set_config

# Configure logging for test traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_xml_content():
    """Create a sample XML file with at least 3 rules and 2 objects for testing."""
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <devices>
    <entry name="test-device">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Web-Server-1">
              <ip-netmask>192.168.1.10/32</ip-netmask>
            </entry>
            <entry name="Database-Server-1">
              <ip-netmask>192.168.2.10/32</ip-netmask>
            </entry>
            <entry name="App-Server-1">
              <ip-netmask>192.168.3.10/32</ip-netmask>
            </entry>
          </address>
          <service>
            <entry name="HTTP-Service">
              <protocol>
                <tcp>
                  <port>80</port>
                </tcp>
              </protocol>
            </entry>
            <entry name="HTTPS-Service">
              <protocol>
                <tcp>
                  <port>443</port>
                </tcp>
              </protocol>
            </entry>
          </service>
          <rulebase>
            <security>
              <rules>
                <entry name="Allow-Web-Traffic">
                  <from><member>trust</member></from>
                  <to><member>untrust</member></to>
                  <source><member>Web-Server-1</member></source>
                  <destination><member>any</member></destination>
                  <service><member>HTTP-Service</member></service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-HTTPS-Traffic">
                  <from><member>trust</member></from>
                  <to><member>untrust</member></to>
                  <source><member>Web-Server-1</member></source>
                  <destination><member>any</member></destination>
                  <service><member>HTTPS-Service</member></service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-Database-Access">
                  <from><member>trust</member></from>
                  <to><member>dmz</member></to>
                  <source><member>App-Server-1</member></source>
                  <destination><member>Database-Server-1</member></destination>
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

def create_malformed_xml_content():
    """Create a malformed XML file for error testing."""
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<config version="10.1.0">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Server-001">
              <ip-netmask>192.168.1.10/32</ip-netmask>
            <!-- Missing closing entry tag -->
          </address>
        </entry>
      </vsys>
    </entry>
  </devices>
<!-- Missing closing config tag -->'''

def create_sample_set_content():
    """Create a sample SET format file with at least 3 rules for testing."""
    return '''set security rules Allow-Web-Traffic from trust to untrust source Web-Server-1 destination any service HTTP-Service action allow
set security rules Allow-HTTPS-Traffic from trust to untrust source Web-Server-1 destination any service HTTPS-Service action allow
set security rules Allow-Database-Access from trust to dmz source App-Server-1 destination Database-Server-1 service Database-Service action allow
set security rules Deny-All-Traffic from any to any source any destination any service any action deny disabled
set address Web-Server-1 ip-netmask 192.168.1.10/32
set address Database-Server-1 ip-netmask 192.168.2.10/32
set address App-Server-1 ip-netmask 192.168.3.10/32
set service HTTP-Service protocol tcp port 80
set service HTTPS-Service protocol tcp port 443
set service Database-Service protocol tcp port 3306'''

def create_malformed_set_content():
    """Create malformed SET commands for error testing."""
    return '''set security rules Allow-Web-Traffic from trust to untrust source Web-Server-1 destination any service HTTP-Service action allow
set security rules incomplete-rule from trust
set invalid-command this is not a valid set command
set address Web-Server-1 ip-netmask invalid-ip-format
set service HTTP-Service protocol tcp port invalid-port'''

class TestXMLParsing:
    """Test cases for XML parsing functions."""

    def test_parse_rules_success(self):
        """Test successful parsing of rules from XML."""
        logger.info("Testing parse_rules with valid XML content")
        
        xml_content = create_sample_xml_content()
        rules = parse_rules(xml_content)
        
        logger.info(f"Parsed {len(rules)} rules from XML")
        
        # Verify we have at least 3 rules as required
        assert len(rules) >= 3, f"Expected at least 3 rules, got {len(rules)}"
        
        # Verify rule structure matches expected dictionary format
        for rule in rules:
            assert isinstance(rule, dict), "Each rule should be a dictionary"
            
            # Check required fields per DBSchema.txt
            required_fields = ["rule_name", "rule_type", "src_zone", "dst_zone", 
                             "src", "dst", "service", "action", "position", "is_disabled"]
            
            for field in required_fields:
                assert field in rule, f"Rule missing required field: {field}"
            
            # Verify field types
            assert isinstance(rule["rule_name"], str), "rule_name should be string"
            assert isinstance(rule["position"], int), "position should be integer"
            assert isinstance(rule["is_disabled"], bool), "is_disabled should be boolean"
            assert rule["action"] in ["allow", "deny", "drop"], f"Invalid action: {rule['action']}"
        
        # Test specific rule content
        rule_names = [rule["rule_name"] for rule in rules]
        assert "Allow-Web-Traffic" in rule_names, "Should contain Allow-Web-Traffic rule"
        assert "Allow-HTTPS-Traffic" in rule_names, "Should contain Allow-HTTPS-Traffic rule"
        assert "Allow-Database-Access" in rule_names, "Should contain Allow-Database-Access rule"
        
        # Test disabled rule handling (optional - may not have disabled rules in simple test)
        disabled_rules = [rule for rule in rules if rule["is_disabled"]]
        logger.info(f"Found {len(disabled_rules)} disabled rules")
        
        logger.info("parse_rules test completed successfully")

    def test_parse_objects_success(self):
        """Test successful parsing of objects from XML."""
        logger.info("Testing parse_objects with valid XML content")
        
        xml_content = create_sample_xml_content()
        objects = parse_objects(xml_content)
        
        logger.info(f"Parsed {len(objects)} objects from XML")
        
        # Verify we have at least 2 objects as required
        assert len(objects) >= 2, f"Expected at least 2 objects, got {len(objects)}"
        
        # Verify object structure matches expected dictionary format
        for obj in objects:
            assert isinstance(obj, dict), "Each object should be a dictionary"
            
            # Check required fields per DBSchema.txt (using actual field names)
            required_fields = ["name", "object_type", "value"]

            for field in required_fields:
                assert field in obj, f"Object missing required field: {field}"

            # Verify field types
            assert isinstance(obj["name"], str), "name should be string"
            assert isinstance(obj["object_type"], str), "object_type should be string"
            assert obj["object_type"] in ["address", "service"], f"Invalid object type: {obj['object_type']}"
        
        # Test specific object content
        object_names = [obj["name"] for obj in objects]
        assert "Web-Server-1" in object_names, "Should contain Web-Server-1 address object"
        assert "HTTP-Service" in object_names, "Should contain HTTP-Service service object"
        
        # Verify address objects have IP values
        address_objects = [obj for obj in objects if obj["object_type"] == "address"]
        assert len(address_objects) >= 3, "Should have at least 3 address objects"

        for addr_obj in address_objects:
            assert "192.168." in addr_obj["value"], f"Address object should have IP value: {addr_obj['value']}"

        # Verify service objects have port values
        service_objects = [obj for obj in objects if obj["object_type"] == "service"]
        assert len(service_objects) >= 2, "Should have at least 2 service objects"
        
        logger.info("parse_objects test completed successfully")

    def test_parse_metadata_success(self):
        """Test successful parsing of metadata from XML."""
        logger.info("Testing parse_metadata with valid XML content")
        
        xml_content = create_sample_xml_content()
        metadata = parse_metadata(xml_content)
        
        logger.info(f"Parsed metadata with {len(metadata)} fields")
        
        # Verify metadata is a dictionary
        assert isinstance(metadata, dict), "Metadata should be a dictionary"
        
        # Check for expected metadata fields
        expected_fields = ["firmware_version", "rule_count", "address_object_count", "service_object_count"]
        
        for field in expected_fields:
            assert field in metadata, f"Metadata missing expected field: {field}"
        
        # Verify field types and values
        assert isinstance(metadata["rule_count"], int), "rule_count should be integer"
        assert isinstance(metadata["address_object_count"], int), "address_object_count should be integer"
        assert isinstance(metadata["service_object_count"], int), "service_object_count should be integer"
        
        # Verify counts match our test data
        assert metadata["rule_count"] >= 3, f"Expected at least 3 rules, metadata shows {metadata['rule_count']}"
        assert metadata["address_object_count"] >= 3, f"Expected at least 3 address objects, metadata shows {metadata['address_object_count']}"
        assert metadata["service_object_count"] >= 2, f"Expected at least 2 service objects, metadata shows {metadata['service_object_count']}"
        
        logger.info("parse_metadata test completed successfully")

    def test_parse_rules_malformed_xml(self):
        """Test error handling with malformed XML for parse_rules."""
        logger.info("Testing parse_rules error handling with malformed XML")
        
        malformed_content = create_malformed_xml_content()
        
        with pytest.raises(ValueError) as exc_info:
            parse_rules(malformed_content)
        
        error_message = str(exc_info.value)
        assert "Malformed XML" in error_message, f"Expected 'Malformed XML' in error message: {error_message}"
        
        logger.info(f"parse_rules correctly raised ValueError: {error_message}")

    def test_parse_objects_malformed_xml(self):
        """Test error handling with malformed XML for parse_objects."""
        logger.info("Testing parse_objects error handling with malformed XML")
        
        malformed_content = create_malformed_xml_content()
        
        with pytest.raises(ValueError) as exc_info:
            parse_objects(malformed_content)
        
        error_message = str(exc_info.value)
        assert "Malformed XML" in error_message, f"Expected 'Malformed XML' in error message: {error_message}"
        
        logger.info(f"parse_objects correctly raised ValueError: {error_message}")

    def test_parse_metadata_malformed_xml(self):
        """Test error handling with malformed XML for parse_metadata."""
        logger.info("Testing parse_metadata error handling with malformed XML")
        
        malformed_content = create_malformed_xml_content()
        
        with pytest.raises(ValueError) as exc_info:
            parse_metadata(malformed_content)
        
        error_message = str(exc_info.value)
        assert "Malformed XML" in error_message, f"Expected 'Malformed XML' in error message: {error_message}"
        
        logger.info(f"parse_metadata correctly raised ValueError: {error_message}")

    def test_empty_xml_content(self):
        """Test handling of empty XML content."""
        logger.info("Testing parsing functions with empty content")
        
        empty_content = b""
        
        # All parsing functions should raise ValueError for empty content
        with pytest.raises(ValueError) as exc_info:
            parse_rules(empty_content)
        assert "XML content is empty" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            parse_objects(empty_content)
        assert "XML content is empty" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            parse_metadata(empty_content)
        assert "XML content is empty" in str(exc_info.value)
        
        logger.info("Empty content handling test completed successfully")

class TestSETFormatParsing:
    """Test cases for SET format parsing functions (Task 16)."""

    def test_parse_set_config_success(self):
        """Test successful parsing of SET format configuration."""
        logger.info("Testing parse_set_config with valid SET content")

        set_content = create_sample_set_content()
        rules, objects, metadata = parse_set_config(set_content)

        logger.info(f"Parsed {len(rules)} rules, {len(objects)} objects from SET format")

        # Verify we have at least 3 rules as required
        assert len(rules) >= 3, f"Expected at least 3 rules, got {len(rules)}"

        # Verify rule structure matches XML parser output for consistency
        for rule in rules:
            assert isinstance(rule, dict), "Each rule should be a dictionary"

            # Check required fields match XML parser structure
            required_fields = ["rule_name", "rule_type", "src_zone", "dst_zone",
                             "src", "dst", "service", "action", "position", "is_disabled"]

            for field in required_fields:
                assert field in rule, f"Rule missing required field: {field}"

            # Verify field types match XML parser
            assert isinstance(rule["rule_name"], str), "rule_name should be string"
            assert isinstance(rule["position"], int), "position should be integer"
            assert isinstance(rule["is_disabled"], bool), "is_disabled should be boolean"
            assert rule["action"] in ["allow", "deny", "drop"], f"Invalid action: {rule['action']}"

        # Verify objects structure matches XML parser output
        for obj in objects:
            assert isinstance(obj, dict), "Each object should be a dictionary"

            required_fields = ["name", "object_type", "value"]
            for field in required_fields:
                assert field in obj, f"Object missing required field: {field}"

            assert obj["object_type"] in ["address", "service"], f"Invalid object type: {obj['object_type']}"

        # Verify metadata structure matches XML parser output
        assert isinstance(metadata, dict), "Metadata should be a dictionary"

        logger.info("parse_set_config test completed successfully")

    def test_parse_set_config_consistency_with_xml(self):
        """Test that SET parser output structure is consistent with XML parser."""
        logger.info("Testing SET parser consistency with XML parser structure")

        # Parse XML content
        xml_content = create_sample_xml_content()
        xml_rules = parse_rules(xml_content)
        xml_objects = parse_objects(xml_content)
        xml_metadata = parse_metadata(xml_content)

        # Parse equivalent SET content
        set_content = create_sample_set_content()
        set_rules, set_objects, set_metadata = parse_set_config(set_content)

        # Verify structure consistency
        if xml_rules and set_rules:
            xml_rule_keys = set(xml_rules[0].keys())
            set_rule_keys = set(set_rules[0].keys())
            assert xml_rule_keys == set_rule_keys, f"Rule structure mismatch: XML={xml_rule_keys}, SET={set_rule_keys}"

        if xml_objects and set_objects:
            xml_obj_keys = set(xml_objects[0].keys())
            set_obj_keys = set(set_objects[0].keys())
            assert xml_obj_keys == set_obj_keys, f"Object structure mismatch: XML={xml_obj_keys}, SET={set_obj_keys}"

        # Verify metadata has similar structure
        common_metadata_fields = ["rule_count", "address_object_count", "service_object_count"]
        for field in common_metadata_fields:
            if field in xml_metadata:
                assert field in set_metadata, f"SET metadata missing field present in XML: {field}"

        logger.info("SET parser consistency test completed successfully")

    def test_parse_set_config_malformed_commands(self):
        """Test error handling for malformed SET commands."""
        logger.info("Testing parse_set_config error handling with malformed commands")

        malformed_content = create_malformed_set_content()

        # Should handle malformed commands gracefully or raise descriptive error
        try:
            rules, objects, metadata = parse_set_config(malformed_content)

            # If it doesn't raise an error, it should at least parse valid commands
            # and skip/log invalid ones
            logger.info(f"Parsed {len(rules)} rules, {len(objects)} objects from malformed SET content")

            # Should have parsed at least the valid commands
            assert len(rules) >= 1, "Should parse at least one valid rule"

        except ValueError as e:
            # If it raises an error, it should be descriptive
            error_message = str(e)
            assert len(error_message) > 10, f"Error message should be descriptive: {error_message}"
            logger.info(f"parse_set_config correctly raised descriptive error: {error_message}")

        logger.info("Malformed SET commands test completed")

    def test_parse_set_config_empty_content(self):
        """Test handling of empty SET content."""
        logger.info("Testing parse_set_config with empty content")

        empty_content = ""

        try:
            rules, objects, metadata = parse_set_config(empty_content)

            # Should return empty lists/dict for empty content
            assert isinstance(rules, list), "Rules should be a list"
            assert isinstance(objects, list), "Objects should be a list"
            assert isinstance(metadata, dict), "Metadata should be a dictionary"

            logger.info("Empty SET content handled gracefully")

        except ValueError as e:
            # If it raises an error, it should be descriptive
            error_message = str(e)
            assert "empty" in error_message.lower(), f"Error should mention empty content: {error_message}"
            logger.info(f"parse_set_config correctly raised error for empty content: {error_message}")

    def test_parse_set_config_specific_rules(self):
        """Test parsing of specific SET rule formats."""
        logger.info("Testing parse_set_config with specific rule formats")

        set_content = create_sample_set_content()
        rules, objects, metadata = parse_set_config(set_content)

        # Test specific rule names
        rule_names = [rule["rule_name"] for rule in rules]
        expected_rules = ["Allow-Web-Traffic", "Allow-HTTPS-Traffic", "Allow-Database-Access"]

        for expected_rule in expected_rules:
            assert expected_rule in rule_names, f"Should contain rule: {expected_rule}"

        # Test disabled rule handling
        disabled_rules = [rule for rule in rules if rule["is_disabled"]]
        if disabled_rules:
            logger.info(f"Found {len(disabled_rules)} disabled rules")

        # Test object parsing
        object_names = [obj["name"] for obj in objects]
        logger.info(f"Found objects: {object_names}")

        # Check for address objects
        address_objects = [obj for obj in objects if obj["object_type"] == "address"]
        assert len(address_objects) >= 3, f"Should have at least 3 address objects, got {len(address_objects)}"

        # Check for service objects
        service_objects = [obj for obj in objects if obj["object_type"] == "service"]
        assert len(service_objects) >= 3, f"Should have at least 3 service objects, got {len(service_objects)}"

        # Verify specific address object exists
        address_names = [obj["name"] for obj in address_objects]
        assert "Web-Server-1" in address_names, f"Should contain Web-Server-1 address object"

        logger.info("Specific SET rule format test completed successfully")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
