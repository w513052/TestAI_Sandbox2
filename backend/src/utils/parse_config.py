import hashlib
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from src.utils.logging import logger

def validate_xml_file(file_content: bytes) -> bool:
    """
    Validate XML file structure before parsing.

    Args:
        file_content: Raw file content as bytes

    Returns:
        bool: True if valid XML with config root element

    Raises:
        ValueError: If XML is invalid or missing config root
    """
    try:
        root = ET.fromstring(file_content)
        if root.tag != "config":
            raise ValueError("XML file must have a <config> root element")
        logger.info("XML file validation successful")
        return True
    except ET.ParseError as e:
        logger.error(f"XML syntax error: {str(e)}")
        raise ValueError(f"Invalid XML syntax: {str(e)}")
    except Exception as e:
        logger.error(f"XML validation error: {str(e)}")
        raise ValueError(f"XML validation failed: {str(e)}")

def compute_file_hash(file_content: bytes) -> str:
    """
    Compute SHA256 hash of file content.
    
    Args:
        file_content: Raw file content as bytes
        
    Returns:
        str: SHA256 hash as hexadecimal string
    """
    return hashlib.sha256(file_content).hexdigest()

def parse_rules(xml_content: bytes) -> List[Dict[str, Any]]:
    """
    Extract security rules from XML config.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        List of dictionaries containing rule data
    """
    try:
        root = ET.fromstring(xml_content)
        rules = []

        # Find security rules - need to traverse the tree manually since ElementTree doesn't support XPath
        for devices in root.findall(".//devices"):
            for device in devices.findall("entry"):
                for vsys in device.findall(".//vsys"):
                    for vsys_entry in vsys.findall("entry"):
                        for rulebase in vsys_entry.findall(".//rulebase"):
                            for security in rulebase.findall("security"):
                                for rules_section in security.findall("rules"):
                                    rule_entries = rules_section.findall("entry")

                                    for i, entry in enumerate(rule_entries):
                                        rule_name = entry.get("name", f"rule_{i}")

                                        # Extract rule attributes with defaults
                                        from_elem = entry.find("from")
                                        src_zone = from_elem.find("member").text if from_elem is not None and from_elem.find("member") is not None else "any"

                                        to_elem = entry.find("to")
                                        dst_zone = to_elem.find("member").text if to_elem is not None and to_elem.find("member") is not None else "any"

                                        source_elem = entry.find("source")
                                        src = source_elem.find("member").text if source_elem is not None and source_elem.find("member") is not None else "any"

                                        dest_elem = entry.find("destination")
                                        dst = dest_elem.find("member").text if dest_elem is not None and dest_elem.find("member") is not None else "any"

                                        service_elem = entry.find("service")
                                        service = service_elem.find("member").text if service_elem is not None and service_elem.find("member") is not None else "any"

                                        action_elem = entry.find("action")
                                        action = action_elem.text if action_elem is not None else "allow"

                                        disabled_elem = entry.find("disabled")
                                        is_disabled = disabled_elem is not None and disabled_elem.text == "yes"

                                        rule_data = {
                                            "rule_name": rule_name,
                                            "rule_type": "security",
                                            "src_zone": src_zone,
                                            "dst_zone": dst_zone,
                                            "src": src,
                                            "dst": dst,
                                            "service": service,
                                            "action": action,
                                            "position": len(rules) + 1,
                                            "is_disabled": is_disabled,
                                            "raw_xml": ET.tostring(entry, encoding='unicode')
                                        }

                                        rules.append(rule_data)

        logger.info(f"Parsed {len(rules)} security rules")
        return rules

    except Exception as e:
        logger.error(f"Error parsing rules: {str(e)}")
        raise ValueError(f"Failed to parse rules: {str(e)}")

def parse_objects(xml_content: bytes) -> List[Dict[str, Any]]:
    """
    Extract address and service objects from XML config.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        List of dictionaries containing object data
    """
    try:
        root = ET.fromstring(xml_content)
        objects = []

        # Parse address objects - traverse manually
        for devices in root.findall(".//devices"):
            for device in devices.findall("entry"):
                for vsys in device.findall(".//vsys"):
                    for vsys_entry in vsys.findall("entry"):
                        for address in vsys_entry.findall(".//address"):
                            for entry in address.findall("entry"):
                                name = entry.get("name", "")

                                # Try to find ip-netmask or fqdn
                                ip_netmask = entry.find("ip-netmask")
                                fqdn = entry.find("fqdn")
                                value = ""
                                if ip_netmask is not None:
                                    value = ip_netmask.text or ""
                                elif fqdn is not None:
                                    value = fqdn.text or ""

                                object_data = {
                                    "object_type": "address",
                                    "name": name,
                                    "value": value,
                                    "used_in_rules": 0,
                                    "raw_xml": ET.tostring(entry, encoding='unicode')
                                }
                                objects.append(object_data)

                        # Parse service objects
                        for service in vsys_entry.findall(".//service"):
                            for entry in service.findall("entry"):
                                name = entry.get("name", "")

                                # Try to find protocol/tcp/port or protocol/udp/port
                                protocol = ""
                                protocol_elem = entry.find("protocol")
                                if protocol_elem is not None:
                                    tcp_elem = protocol_elem.find("tcp")
                                    udp_elem = protocol_elem.find("udp")
                                    if tcp_elem is not None:
                                        port_elem = tcp_elem.find("port")
                                        if port_elem is not None:
                                            protocol = f"tcp/{port_elem.text}"
                                    elif udp_elem is not None:
                                        port_elem = udp_elem.find("port")
                                        if port_elem is not None:
                                            protocol = f"udp/{port_elem.text}"

                                object_data = {
                                    "object_type": "service",
                                    "name": name,
                                    "value": protocol,
                                    "used_in_rules": 0,
                                    "raw_xml": ET.tostring(entry, encoding='unicode')
                                }
                                objects.append(object_data)

        logger.info(f"Parsed {len(objects)} objects")
        return objects

    except Exception as e:
        logger.error(f"Error parsing objects: {str(e)}")
        raise ValueError(f"Failed to parse objects: {str(e)}")

def parse_metadata(xml_content: bytes) -> Dict[str, Any]:
    """
    Extract metadata from XML config.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        Dictionary containing metadata
    """
    try:
        root = ET.fromstring(xml_content)
        metadata = {}

        # Extract firmware version - traverse manually
        version = "unknown"
        for devices in root.findall(".//devices"):
            for device in devices.findall("entry"):
                for deviceconfig in device.findall("deviceconfig"):
                    for system in deviceconfig.findall("system"):
                        version_elem = system.find("version")
                        if version_elem is not None:
                            version = version_elem.text or "unknown"
                            break

        metadata["firmware_version"] = version

        # Count rules and objects by parsing the structure
        rule_count = 0
        address_count = 0
        service_count = 0

        for devices in root.findall(".//devices"):
            for device in devices.findall("entry"):
                for vsys in device.findall(".//vsys"):
                    for vsys_entry in vsys.findall("entry"):
                        # Count rules
                        for rulebase in vsys_entry.findall(".//rulebase"):
                            for security in rulebase.findall("security"):
                                for rules_section in security.findall("rules"):
                                    rule_count += len(rules_section.findall("entry"))

                        # Count address objects
                        for address in vsys_entry.findall(".//address"):
                            address_count += len(address.findall("entry"))

                        # Count service objects
                        for service in vsys_entry.findall(".//service"):
                            service_count += len(service.findall("entry"))

        metadata["rule_count"] = rule_count
        metadata["address_object_count"] = address_count
        metadata["service_object_count"] = service_count

        logger.info("Metadata extraction successful")
        return metadata

    except Exception as e:
        logger.error(f"Error parsing metadata: {str(e)}")
        return {}
