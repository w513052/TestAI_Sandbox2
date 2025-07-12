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

def store_rules(db_session, audit_id: int, rules_data: List[Dict[str, Any]]) -> int:
    """
    Store parsed rules to the FirewallRule table with batch operations.

    Args:
        db_session: SQLAlchemy database session
        audit_id: ID of the audit session
        rules_data: List of dictionaries containing rule data

    Returns:
        int: Number of rules successfully stored

    Raises:
        ValueError: If required fields are missing
        Exception: For database errors
    """
    if not rules_data:
        logger.info("No rules to store")
        return 0

    try:
        from src.models import FirewallRule

        # Validate and prepare rules for batch insert
        validated_rules = []
        for i, rule_data in enumerate(rules_data):
            try:
                # Validate required fields
                required_fields = ['rule_name', 'rule_type', 'position']
                for field in required_fields:
                    if field not in rule_data:
                        logger.error(f"Missing required field '{field}' in rule {i}")
                        continue

                # Prepare rule data with audit_id
                rule_record = {
                    'audit_id': audit_id,
                    'rule_name': rule_data.get('rule_name', f'rule_{i}')[:255],  # Truncate if too long
                    'rule_type': rule_data.get('rule_type', 'security')[:50],
                    'src_zone': rule_data.get('src_zone', 'any')[:255],
                    'dst_zone': rule_data.get('dst_zone', 'any')[:255],
                    'src': rule_data.get('src', 'any'),  # Text field, no length limit
                    'dst': rule_data.get('dst', 'any'),  # Text field, no length limit
                    'service': rule_data.get('service', 'any'),  # Text field, no length limit
                    'action': rule_data.get('action', 'allow')[:50],
                    'position': rule_data.get('position', i + 1),
                    'is_disabled': rule_data.get('is_disabled', False),
                    'raw_xml': rule_data.get('raw_xml', '')  # Text field, no length limit
                }

                validated_rules.append(rule_record)

            except Exception as e:
                logger.error(f"Error validating rule {i} '{rule_data.get('rule_name', 'unknown')}': {str(e)}")
                continue

        if not validated_rules:
            logger.warning("No valid rules to store after validation")
            return 0

        # Perform batch insert
        logger.info(f"Performing batch insert of {len(validated_rules)} rules")

        # Use bulk_insert_mappings for better performance
        db_session.bulk_insert_mappings(FirewallRule, validated_rules)

        logger.info(f"Successfully stored {len(validated_rules)} out of {len(rules_data)} rules")
        return len(validated_rules)

    except Exception as e:
        logger.error(f"Database error during rules storage: {str(e)}")
        raise Exception(f"Failed to store rules: {str(e)}")

def store_objects(db_session, audit_id: int, objects_data: List[Dict[str, Any]]) -> int:
    """
    Store parsed objects to the ObjectDefinition table with batch operations.

    Args:
        db_session: SQLAlchemy database session
        audit_id: ID of the audit session
        objects_data: List of dictionaries containing object data

    Returns:
        int: Number of objects successfully stored

    Raises:
        ValueError: If required fields are missing
        Exception: For database errors
    """
    if not objects_data:
        logger.info("No objects to store")
        return 0

    try:
        from src.models import ObjectDefinition

        # Valid object types for validation
        valid_object_types = ['address', 'service', 'application', 'schedule', 'tag']

        # Track object statistics
        object_stats = {'address': 0, 'service': 0, 'other': 0}
        duplicate_names = set()

        # Validate and prepare objects for batch insert
        validated_objects = []
        seen_objects = set()  # Track duplicates within this batch

        for i, object_data in enumerate(objects_data):
            try:
                # Validate required fields
                required_fields = ['object_type', 'name']
                for field in required_fields:
                    if field not in object_data:
                        logger.error(f"Missing required field '{field}' in object {i}")
                        continue

                # Validate object type
                object_type = object_data.get('object_type', 'unknown').lower()
                if object_type not in valid_object_types:
                    logger.warning(f"Unknown object type '{object_type}' for object '{object_data.get('name', 'unknown')}', storing as-is")

                # Check for duplicates within this batch
                object_key = (object_type, object_data.get('name', ''))
                if object_key in seen_objects:
                    duplicate_names.add(object_data.get('name', f'object_{i}'))
                    logger.warning(f"Duplicate object found in batch: {object_key}")
                    continue
                seen_objects.add(object_key)

                # Prepare object data with audit_id
                object_record = {
                    'audit_id': audit_id,
                    'object_type': object_type[:50],
                    'name': object_data.get('name', f'object_{i}')[:255],
                    'value': object_data.get('value', ''),  # Text field, no length limit
                    'used_in_rules': object_data.get('used_in_rules', 0),
                    'raw_xml': object_data.get('raw_xml', '')  # Text field, no length limit
                }

                validated_objects.append(object_record)

                # Update statistics
                if object_type in object_stats:
                    object_stats[object_type] += 1
                else:
                    object_stats['other'] += 1

            except Exception as e:
                logger.error(f"Error validating object {i} '{object_data.get('name', 'unknown')}': {str(e)}")
                continue

        if not validated_objects:
            logger.warning("No valid objects to store after validation")
            return 0

        # Log object statistics
        logger.info(f"Object validation completed: {len(validated_objects)} valid objects")
        logger.info(f"Object breakdown: Address={object_stats['address']}, Service={object_stats['service']}, Other={object_stats['other']}")
        if duplicate_names:
            logger.warning(f"Found {len(duplicate_names)} duplicate object names: {list(duplicate_names)[:5]}...")

        # Perform batch insert
        logger.info(f"Performing batch insert of {len(validated_objects)} objects")

        # Use bulk_insert_mappings for better performance
        db_session.bulk_insert_mappings(ObjectDefinition, validated_objects)

        logger.info(f"Successfully stored {len(validated_objects)} out of {len(objects_data)} objects")
        return len(validated_objects)

    except Exception as e:
        logger.error(f"Database error during objects storage: {str(e)}")
        raise Exception(f"Failed to store objects: {str(e)}")

def analyze_object_usage(rules_data: List[Dict[str, Any]], objects_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze which objects are used in rules and update usage counts.

    Args:
        rules_data: List of parsed rules
        objects_data: List of parsed objects

    Returns:
        Dictionary mapping object names to usage counts
    """
    try:
        # Create a mapping of object names for quick lookup
        object_usage = {}
        object_names = {obj.get('name', '') for obj in objects_data}

        # Initialize usage counts
        for obj in objects_data:
            object_usage[obj.get('name', '')] = 0

        # Analyze rule references to objects
        for rule in rules_data:
            # Check source references
            src = rule.get('src', '')
            if src in object_names:
                object_usage[src] += 1

            # Check destination references
            dst = rule.get('dst', '')
            if dst in object_names:
                object_usage[dst] += 1

            # Check service references
            service = rule.get('service', '')
            if service in object_names:
                object_usage[service] += 1

        # Update objects_data with usage counts
        for obj in objects_data:
            obj_name = obj.get('name', '')
            if obj_name in object_usage:
                obj['used_in_rules'] = object_usage[obj_name]

        # Log usage statistics
        used_objects = sum(1 for count in object_usage.values() if count > 0)
        unused_objects = len(object_usage) - used_objects

        logger.info(f"Object usage analysis completed: {used_objects} used, {unused_objects} unused objects")

        return object_usage

    except Exception as e:
        logger.error(f"Error analyzing object usage: {str(e)}")
        return {}

def parse_rules_streaming(xml_content: bytes) -> List[Dict[str, Any]]:
    """
    Extract security rules from XML config using streaming parser for large files.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        List of dictionaries containing rule data

    Raises:
        ValueError: If XML parsing fails
    """
    try:
        import io
        from xml.etree.ElementTree import iterparse

        rules = []
        xml_stream = io.BytesIO(xml_content)

        # Track current context for nested parsing
        current_rule = None
        in_rules_section = False
        rule_depth = 0

        logger.info("Starting streaming XML parsing for rules")

        # Use iterparse for memory-efficient streaming
        for event, elem in iterparse(xml_stream, events=('start', 'end')):

            if event == 'start':
                # Detect when we enter a rules section
                if elem.tag == 'rules':
                    # Check if we're in a security context by tracking the path
                    in_rules_section = True
                    logger.debug("Entered security rules section")

                # Detect individual rule entries
                elif elem.tag == 'entry' and in_rules_section:
                    rule_name = elem.get("name", f"rule_{len(rules)}")
                    current_rule = {
                        "rule_name": rule_name,
                        "rule_type": "security",
                        "src_zone": "any",
                        "dst_zone": "any",
                        "src": "any",
                        "dst": "any",
                        "service": "any",
                        "action": "allow",
                        "position": len(rules) + 1,
                        "is_disabled": False,
                        "raw_xml": ""
                    }
                    rule_depth = 0

            elif event == 'end':
                # Process completed rule entry
                if elem.tag == 'entry' and in_rules_section and current_rule is not None:
                    # Extract rule data from completed element
                    current_rule = _extract_rule_data_streaming(elem, current_rule)
                    current_rule["raw_xml"] = ET.tostring(elem, encoding='unicode')

                    rules.append(current_rule)
                    logger.debug(f"Parsed rule: {current_rule['rule_name']}")

                    # Clear memory by removing processed element
                    elem.clear()
                    current_rule = None

                # Exit rules section
                elif elem.tag == 'rules' and in_rules_section:
                    in_rules_section = False
                    logger.debug("Exited security rules section")

                # Clear processed elements to save memory
                elif elem.tag in ['devices', 'vsys', 'rulebase', 'security']:
                    elem.clear()

        logger.info(f"Streaming parser completed: {len(rules)} security rules parsed")
        return rules

    except Exception as e:
        logger.error(f"Error in streaming rules parser: {str(e)}")
        raise ValueError(f"Failed to parse rules with streaming parser: {str(e)}")

def _extract_rule_data_streaming(rule_elem, rule_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to extract rule data from XML element during streaming parse.

    Args:
        rule_elem: XML element containing rule data
        rule_data: Dictionary to populate with rule data

    Returns:
        Updated rule data dictionary
    """
    try:
        # Extract from zone
        from_elem = rule_elem.find("from")
        if from_elem is not None:
            member = from_elem.find("member")
            if member is not None and member.text:
                rule_data["src_zone"] = member.text

        # Extract to zone
        to_elem = rule_elem.find("to")
        if to_elem is not None:
            member = to_elem.find("member")
            if member is not None and member.text:
                rule_data["dst_zone"] = member.text

        # Extract source
        source_elem = rule_elem.find("source")
        if source_elem is not None:
            member = source_elem.find("member")
            if member is not None and member.text:
                rule_data["src"] = member.text

        # Extract destination
        dest_elem = rule_elem.find("destination")
        if dest_elem is not None:
            member = dest_elem.find("member")
            if member is not None and member.text:
                rule_data["dst"] = member.text

        # Extract service
        service_elem = rule_elem.find("service")
        if service_elem is not None:
            member = service_elem.find("member")
            if member is not None and member.text:
                rule_data["service"] = member.text

        # Extract action
        action_elem = rule_elem.find("action")
        if action_elem is not None and action_elem.text:
            rule_data["action"] = action_elem.text

        # Extract disabled status
        disabled_elem = rule_elem.find("disabled")
        if disabled_elem is not None:
            rule_data["is_disabled"] = disabled_elem.text == "yes"

        return rule_data

    except Exception as e:
        logger.warning(f"Error extracting rule data: {str(e)}")
        return rule_data

def parse_objects_streaming(xml_content: bytes) -> List[Dict[str, Any]]:
    """
    Extract address and service objects from XML config using streaming parser for large files.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        List of dictionaries containing object data

    Raises:
        ValueError: If XML parsing fails
    """
    try:
        import io
        from xml.etree.ElementTree import iterparse

        objects = []
        xml_stream = io.BytesIO(xml_content)

        # Track current context for nested parsing
        in_address_section = False
        in_service_section = False
        current_object = None

        logger.info("Starting streaming XML parsing for objects")

        # Use iterparse for memory-efficient streaming
        for event, elem in iterparse(xml_stream, events=('start', 'end')):

            if event == 'start':
                # Detect when we enter address or service sections
                if elem.tag == 'address':
                    # Assume this is a top-level address section
                    in_address_section = True
                    logger.debug("Entered address objects section")

                elif elem.tag == 'service':
                    # Assume this is a top-level service section
                    in_service_section = True
                    logger.debug("Entered service objects section")

                # Detect individual object entries
                elif elem.tag == 'entry':
                    if in_address_section:
                        object_name = elem.get("name", f"address_{len(objects)}")
                        current_object = {
                            "object_type": "address",
                            "name": object_name,
                            "value": "",
                            "used_in_rules": 0,
                            "raw_xml": ""
                        }

                    elif in_service_section:
                        object_name = elem.get("name", f"service_{len(objects)}")
                        current_object = {
                            "object_type": "service",
                            "name": object_name,
                            "value": "",
                            "used_in_rules": 0,
                            "raw_xml": ""
                        }

            elif event == 'end':
                # Process completed object entry
                if elem.tag == 'entry' and current_object is not None:
                    if in_address_section or in_service_section:
                        # Extract object data from completed element
                        current_object = _extract_object_data_streaming(elem, current_object)
                        current_object["raw_xml"] = ET.tostring(elem, encoding='unicode')

                        objects.append(current_object)
                        logger.debug(f"Parsed {current_object['object_type']} object: {current_object['name']}")

                        # Clear memory by removing processed element
                        elem.clear()
                        current_object = None

                # Exit object sections
                elif elem.tag == 'address' and in_address_section:
                    in_address_section = False
                    logger.debug("Exited address objects section")

                elif elem.tag == 'service' and in_service_section:
                    in_service_section = False
                    logger.debug("Exited service objects section")

                # Clear processed elements to save memory
                elif elem.tag in ['devices', 'vsys', 'entry']:
                    elem.clear()

        logger.info(f"Streaming parser completed: {len(objects)} objects parsed")
        return objects

    except Exception as e:
        logger.error(f"Error in streaming objects parser: {str(e)}")
        raise ValueError(f"Failed to parse objects with streaming parser: {str(e)}")

def _extract_object_data_streaming(obj_elem, obj_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to extract object data from XML element during streaming parse.

    Args:
        obj_elem: XML element containing object data
        obj_data: Dictionary to populate with object data

    Returns:
        Updated object data dictionary
    """
    try:
        if obj_data["object_type"] == "address":
            # Extract IP netmask or FQDN
            ip_netmask = obj_elem.find("ip-netmask")
            fqdn = obj_elem.find("fqdn")
            ip_range = obj_elem.find("ip-range")

            if ip_netmask is not None and ip_netmask.text:
                obj_data["value"] = ip_netmask.text
            elif fqdn is not None and fqdn.text:
                obj_data["value"] = fqdn.text
            elif ip_range is not None and ip_range.text:
                obj_data["value"] = ip_range.text

        elif obj_data["object_type"] == "service":
            # Extract protocol and port information
            protocol_elem = obj_elem.find("protocol")
            if protocol_elem is not None:
                tcp_elem = protocol_elem.find("tcp")
                udp_elem = protocol_elem.find("udp")

                if tcp_elem is not None:
                    port_elem = tcp_elem.find("port")
                    if port_elem is not None and port_elem.text:
                        obj_data["value"] = f"tcp/{port_elem.text}"
                elif udp_elem is not None:
                    port_elem = udp_elem.find("port")
                    if port_elem is not None and port_elem.text:
                        obj_data["value"] = f"udp/{port_elem.text}"

        return obj_data

    except Exception as e:
        logger.warning(f"Error extracting object data: {str(e)}")
        return obj_data

def parse_rules_adaptive(xml_content: bytes, force_streaming: bool = False) -> List[Dict[str, Any]]:
    """
    Parse rules using adaptive approach - streaming for large files, regular for small files.

    Args:
        xml_content: Raw XML content as bytes
        force_streaming: Force use of streaming parser regardless of file size

    Returns:
        List of dictionaries containing rule data
    """
    try:
        # Define threshold for streaming (5MB)
        STREAMING_THRESHOLD = 5 * 1024 * 1024  # 5MB
        file_size = len(xml_content)

        use_streaming = force_streaming or file_size > STREAMING_THRESHOLD

        if use_streaming:
            logger.info(f"Using streaming parser for large file ({file_size / 1024 / 1024:.1f}MB)")
            return parse_rules_streaming(xml_content)
        else:
            logger.info(f"Using regular parser for small file ({file_size / 1024:.1f}KB)")
            return parse_rules(xml_content)

    except Exception as e:
        logger.error(f"Error in adaptive rules parsing: {str(e)}")
        # Fallback to regular parser if streaming fails
        if use_streaming:
            logger.warning("Streaming parser failed, falling back to regular parser")
            try:
                return parse_rules(xml_content)
            except Exception as fallback_error:
                logger.error(f"Fallback parser also failed: {str(fallback_error)}")
                raise ValueError(f"Both streaming and regular parsers failed: {str(e)}")
        else:
            raise ValueError(f"Failed to parse rules: {str(e)}")

def parse_objects_adaptive(xml_content: bytes, force_streaming: bool = False) -> List[Dict[str, Any]]:
    """
    Parse objects using adaptive approach - streaming for large files, regular for small files.

    Args:
        xml_content: Raw XML content as bytes
        force_streaming: Force use of streaming parser regardless of file size

    Returns:
        List of dictionaries containing object data
    """
    try:
        # Define threshold for streaming (5MB)
        STREAMING_THRESHOLD = 5 * 1024 * 1024  # 5MB
        file_size = len(xml_content)

        use_streaming = force_streaming or file_size > STREAMING_THRESHOLD

        if use_streaming:
            logger.info(f"Using streaming parser for large file ({file_size / 1024 / 1024:.1f}MB)")
            return parse_objects_streaming(xml_content)
        else:
            logger.info(f"Using regular parser for small file ({file_size / 1024:.1f}KB)")
            return parse_objects(xml_content)

    except Exception as e:
        logger.error(f"Error in adaptive objects parsing: {str(e)}")
        # Fallback to regular parser if streaming fails
        if use_streaming:
            logger.warning("Streaming parser failed, falling back to regular parser")
            try:
                return parse_objects(xml_content)
            except Exception as fallback_error:
                logger.error(f"Fallback parser also failed: {str(fallback_error)}")
                raise ValueError(f"Both streaming and regular parsers failed: {str(e)}")
        else:
            raise ValueError(f"Failed to parse objects: {str(e)}")
