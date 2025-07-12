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

def parse_set_config(set_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parse Palo Alto set-format configuration files.

    Args:
        set_content: Raw set-format content as string

    Returns:
        Tuple of (rules_data, objects_data, metadata)
    """
    try:
        lines = set_content.strip().split('\n')
        rules_data = []
        objects_data = []
        metadata = {"firmware_version": "unknown", "rule_count": 0, "address_object_count": 0, "service_object_count": 0}

        rule_position = 1

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse security rules
            if line.startswith('set security rules') or line.startswith('set rulebase security rules'):
                rule_data = parse_set_rule(line, rule_position)
                if rule_data:
                    rules_data.append(rule_data)
                    rule_position += 1

            # Parse address objects
            elif line.startswith('set address'):
                obj_data = parse_set_address_object(line)
                if obj_data:
                    objects_data.append(obj_data)

            # Parse service objects
            elif line.startswith('set service'):
                obj_data = parse_set_service_object(line)
                if obj_data:
                    objects_data.append(obj_data)

        # Update metadata counts
        metadata["rule_count"] = len(rules_data)
        metadata["address_object_count"] = len([obj for obj in objects_data if obj["object_type"] == "address"])
        metadata["service_object_count"] = len([obj for obj in objects_data if obj["object_type"] == "service"])

        logger.info(f"Parsed {len(rules_data)} security rules from set format")
        logger.info(f"Parsed {len(objects_data)} objects from set format")

        return rules_data, objects_data, metadata

    except Exception as e:
        logger.error(f"Error parsing set config: {str(e)}")
        raise ValueError(f"Failed to parse set config: {str(e)}")

def parse_set_rule(line: str, position: int) -> Dict[str, Any]:
    """
    Parse a single set security rule command.

    Example: set security rules "Allow-Web" from trust to untrust source any destination any service service-http action allow
    """
    try:
        import re

        # Extract rule name (quoted or unquoted)
        name_match = re.search(r'set (?:rulebase )?security rules ["\']?([^"\']+)["\']?', line)
        if not name_match:
            return {}

        rule_name = name_match.group(1).strip()

        # Extract rule attributes using regex patterns
        from_match = re.search(r'from ([^\s]+)', line)
        to_match = re.search(r'to ([^\s]+)', line)
        source_match = re.search(r'source ([^\s]+)', line)
        dest_match = re.search(r'destination ([^\s]+)', line)
        service_match = re.search(r'service ([^\s]+)', line)
        action_match = re.search(r'action ([^\s]+)', line)

        # Check if rule is disabled
        is_disabled = 'disabled yes' in line or 'disable' in line

        rule_data = {
            "rule_name": rule_name,
            "rule_type": "security",
            "src_zone": from_match.group(1) if from_match else "any",
            "dst_zone": to_match.group(1) if to_match else "any",
            "src": source_match.group(1) if source_match else "any",
            "dst": dest_match.group(1) if dest_match else "any",
            "service": service_match.group(1) if service_match else "any",
            "action": action_match.group(1) if action_match else "allow",
            "position": position,
            "is_disabled": is_disabled,
            "raw_xml": line  # Store original set command
        }

        return rule_data

    except Exception as e:
        logger.error(f"Error parsing set rule: {line} - {str(e)}")
        return {}

def parse_set_address_object(line: str) -> Dict[str, Any]:
    """
    Parse a set address object command.

    Examples:
    - set address "Server-1" ip-netmask 192.168.1.100/32
    - set address "Web-Server" fqdn www.example.com
    """
    try:
        import re

        # Extract object name
        name_match = re.search(r'set address ["\']?([^"\']+)["\']?', line)
        if not name_match:
            return {}

        name = name_match.group(1).strip()

        # Extract value (ip-netmask or fqdn)
        value = ""
        if 'ip-netmask' in line:
            ip_match = re.search(r'ip-netmask ([^\s]+)', line)
            if ip_match:
                value = ip_match.group(1)
        elif 'fqdn' in line:
            fqdn_match = re.search(r'fqdn ([^\s]+)', line)
            if fqdn_match:
                value = fqdn_match.group(1)

        return {
            "object_type": "address",
            "name": name,
            "value": value,
            "used_in_rules": 0,
            "raw_xml": line
        }

    except Exception as e:
        logger.error(f"Error parsing set address object: {line} - {str(e)}")
        return {}

def parse_set_service_object(line: str) -> Dict[str, Any]:
    """
    Parse a set service object command.

    Example: set service "HTTP-Custom" protocol tcp port 8080
    """
    try:
        import re

        # Extract object name
        name_match = re.search(r'set service ["\']?([^"\']+)["\']?', line)
        if not name_match:
            return {}

        name = name_match.group(1).strip()

        # Extract protocol and port
        protocol = ""
        port = ""

        protocol_match = re.search(r'protocol ([^\s]+)', line)
        if protocol_match:
            protocol = protocol_match.group(1)

        port_match = re.search(r'port ([^\s]+)', line)
        if port_match:
            port = port_match.group(1)

        value = f"{protocol}/{port}" if protocol and port else protocol or port

        return {
            "object_type": "service",
            "name": name,
            "value": value,
            "used_in_rules": 0,
            "raw_xml": line
        }

    except Exception as e:
        logger.error(f"Error parsing set service object: {line} - {str(e)}")
        return {}
