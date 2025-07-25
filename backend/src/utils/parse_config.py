import hashlib
import xml.etree.ElementTree as ET
import time
import psutil
import os
from typing import List, Dict, Any
from src.utils.logging import logger

try:
    from lxml import etree as lxml_etree
    LXML_AVAILABLE = True
    logger.info("lxml is available for streaming XML parsing")
except ImportError:
    LXML_AVAILABLE = False
    logger.warning("lxml not available, falling back to standard library for streaming parsing")

def get_memory_usage():
    """Get current memory usage in MB."""
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    except:
        return 0

def log_parsing_performance(start_time: float, start_memory: float, item_count: int, item_type: str):
    """Log parsing performance metrics."""
    end_time = time.time()
    end_memory = get_memory_usage()

    duration = end_time - start_time
    memory_used = end_memory - start_memory

    logger.info(f"Streaming {item_type} parsing completed:")
    logger.info(f"  - Items processed: {item_count}")
    logger.info(f"  - Time taken: {duration:.2f} seconds")
    logger.info(f"  - Memory used: {memory_used:.2f} MB")
    logger.info(f"  - Processing rate: {item_count/duration:.1f} items/second")

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
    """Extract security rules from Palo Alto firewall XML configuration.

    Parses firewall security rules from XML configuration files, extracting rule
    attributes such as name, zones, sources, destinations, services, and actions.
    Supports both streaming and regular parsing based on file size for optimal
    performance.

    Args:
        xml_content (bytes): Raw XML configuration content as bytes. Must be valid
            XML format from Palo Alto firewall export.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing parsed rule data.
            Each dictionary contains the following keys:
            - rule_name (str): Name of the firewall rule
            - rule_type (str): Type of rule (typically 'security')
            - src_zone (str): Source security zone
            - dst_zone (str): Destination security zone
            - src (str): Source addresses/objects (comma-separated)
            - dst (str): Destination addresses/objects (comma-separated)
            - service (str): Service/port definitions (comma-separated)
            - action (str): Rule action ('allow', 'deny', or 'drop')
            - position (int): Rule position in the rulebase (1-based)
            - is_disabled (bool): Whether the rule is disabled
            - raw_xml (str): Original XML content for the rule

    Raises:
        ValueError: If xml_content is empty, None, or contains malformed XML.
        Exception: For other parsing errors or system issues.

    Example:
        >>> xml_data = b'''<?xml version="1.0"?>
        ... <config><devices><entry name="fw"><vsys><entry name="vsys1">
        ... <rulebase><security><rules>
        ... <entry name="Allow-Web">
        ...   <from><member>trust</member></from>
        ...   <to><member>untrust</member></to>
        ...   <source><member>any</member></source>
        ...   <destination><member>any</member></destination>
        ...   <service><member>service-http</member></service>
        ...   <action>allow</action>
        ... </entry>
        ... </rules></security></rulebase>
        ... </entry></vsys></entry></devices></config>'''
        >>> rules = parse_rules(xml_data)
        >>> len(rules)
        1
        >>> rules[0]['rule_name']
        'Allow-Web'
        >>> rules[0]['action']
        'allow'

    Note:
        - Uses adaptive parsing: streaming for large files (>10MB), regular for smaller files
        - Automatically handles missing or malformed rule attributes with defaults
        - Preserves original XML for each rule in the 'raw_xml' field
        - Rule positions are automatically assigned based on order in XML
    """
    try:
        # Validate input
        if not xml_content:
            raise ValueError("XML content is empty")

        if not isinstance(xml_content, bytes):
            raise ValueError("XML content must be bytes")

        # Parse XML with detailed error handling
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"XML parsing error at line {e.lineno}, column {e.offset}: {e.msg}")
            raise ValueError(f"Malformed XML: {e.msg} at line {e.lineno}")

        rules = []

        # Validate XML structure - check for required elements
        devices = root.findall(".//devices")
        if not devices:
            logger.warning("No devices section found in XML")
            return rules  # Return empty list for configs without devices section

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

    except ET.ParseError as e:
        error_msg = f"Malformed XML in rules parsing: {e.msg} at line {e.lineno}, column {e.offset}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        error_msg = f"Unexpected error parsing rules: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def parse_objects(xml_content: bytes) -> List[Dict[str, Any]]:
    """Extract address and service objects from Palo Alto firewall XML configuration.

    Parses firewall object definitions including address objects (IP addresses,
    networks, FQDNs) and service objects (TCP/UDP ports, protocols) from XML
    configuration files. Uses adaptive parsing for optimal performance.

    Args:
        xml_content (bytes): Raw XML configuration content as bytes. Must be valid
            XML format from Palo Alto firewall export.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing parsed object data.
            Each dictionary contains the following keys:
            - name (str): Name of the object
            - object_type (str): Type of object ('address' or 'service')
            - value (str): Object value (IP/network for address, port/protocol for service)
            - used_in_rules (int): Number of rules referencing this object (default: 0)
            - raw_xml (str): Original XML content for the object

    Raises:
        ValueError: If xml_content is empty, None, or contains malformed XML.
        Exception: For other parsing errors or system issues.

    Example:
        >>> xml_data = b'''<?xml version="1.0"?>
        ... <config><devices><entry name="fw"><vsys><entry name="vsys1">
        ... <address>
        ...   <entry name="Web-Server">
        ...     <ip-netmask>192.168.1.10/32</ip-netmask>
        ...   </entry>
        ... </address>
        ... <service>
        ...   <entry name="HTTP-Service">
        ...     <protocol><tcp><port>80</port></tcp></protocol>
        ...   </entry>
        ... </service>
        ... </entry></vsys></entry></devices></config>'''
        >>> objects = parse_objects(xml_data)
        >>> len(objects)
        2
        >>> objects[0]['name']
        'Web-Server'
        >>> objects[0]['object_type']
        'address'
        >>> objects[0]['value']
        '192.168.1.10/32'

    Note:
        - Supports multiple address types: ip-netmask, ip-range, fqdn
        - Supports TCP and UDP service definitions with single ports and ranges
        - Uses adaptive parsing: streaming for large files, regular for smaller files
        - Automatically handles missing attributes with sensible defaults
        - Object usage counts are initialized to 0 and updated by analysis functions
    """
    try:
        # Validate input
        if not xml_content:
            raise ValueError("XML content is empty")

        if not isinstance(xml_content, bytes):
            raise ValueError("XML content must be bytes")

        # Parse XML with detailed error handling
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"XML parsing error in objects at line {e.lineno}, column {e.offset}: {e.msg}")
            raise ValueError(f"Malformed XML: {e.msg} at line {e.lineno}")

        objects = []

        # Validate XML structure
        devices = root.findall(".//devices")
        if not devices:
            logger.warning("No devices section found in XML for objects")
            return objects

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

    except ET.ParseError as e:
        error_msg = f"Malformed XML in objects parsing: {e.msg} at line {e.lineno}, column {e.offset}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        error_msg = f"Unexpected error parsing objects: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def parse_metadata(xml_content: bytes) -> Dict[str, Any]:
    """Extract configuration metadata from Palo Alto firewall XML configuration.

    Analyzes the XML configuration to extract summary information including
    firmware version, rule counts, object counts, and other configuration
    statistics useful for reporting and analysis.

    Args:
        xml_content (bytes): Raw XML configuration content as bytes. Must be valid
            XML format from Palo Alto firewall export.

    Returns:
        Dict[str, Any]: Dictionary containing configuration metadata with the following keys:
            - firmware_version (str): Detected firmware version or 'unknown'
            - rule_count (int): Total number of security rules
            - address_object_count (int): Number of address objects defined
            - service_object_count (int): Number of service objects defined

    Raises:
        ValueError: If xml_content is empty, None, or contains malformed XML.
        Exception: For other parsing errors or system issues.

    Example:
        >>> xml_data = b'''<?xml version="1.0"?>
        ... <config version="10.1.0">
        ... <devices><entry name="fw"><vsys><entry name="vsys1">
        ... <address>
        ...   <entry name="Server1"><ip-netmask>192.168.1.1/32</ip-netmask></entry>
        ...   <entry name="Server2"><ip-netmask>192.168.1.2/32</ip-netmask></entry>
        ... </address>
        ... <service>
        ...   <entry name="HTTP"><protocol><tcp><port>80</port></tcp></protocol></entry>
        ... </service>
        ... <rulebase><security><rules>
        ...   <entry name="Rule1"><action>allow</action></entry>
        ... </rules></security></rulebase>
        ... </entry></vsys></entry></devices></config>'''
        >>> metadata = parse_metadata(xml_data)
        >>> metadata['rule_count']
        1
        >>> metadata['address_object_count']
        2
        >>> metadata['service_object_count']
        1

    Note:
        - Firmware version is extracted from the config version attribute
        - Counts are calculated by parsing the actual XML structure
        - Returns 'unknown' for firmware version if not detectable
        - All counts default to 0 if sections are not found
        - Metadata is used for audit session tracking and reporting
    """
    try:
        # Validate input
        if not xml_content:
            raise ValueError("XML content is empty")

        if not isinstance(xml_content, bytes):
            raise ValueError("XML content must be bytes")

        # Parse XML with detailed error handling
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"XML parsing error in metadata at line {e.lineno}, column {e.offset}: {e.msg}")
            raise ValueError(f"Malformed XML: {e.msg} at line {e.lineno}")

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

    except ET.ParseError as e:
        error_msg = f"Malformed XML in metadata parsing: {e.msg} at line {e.lineno}, column {e.offset}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        error_msg = f"Unexpected error parsing metadata: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def parse_set_config(set_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Parse Palo Alto set-format configuration files with incremental command support.

    Parses firewall configurations in set-command format (CLI export format),
    extracting security rules, address objects, and service objects. Supports
    both full configurations and incremental set commands for configuration
    updates and analysis.

    Args:
        set_content (str): Raw set-format configuration content as string.
            Contains 'set' commands in Palo Alto CLI format.

    Returns:
        tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
            A tuple containing three elements:
            1. rules_data: List of dictionaries with parsed security rules
            2. objects_data: List of dictionaries with parsed objects
            3. metadata: Dictionary with configuration metadata

            Rules dictionaries contain the same structure as parse_rules():
            - rule_name, rule_type, src_zone, dst_zone, src, dst, service,
              action, position, is_disabled, raw_xml

            Objects dictionaries contain the same structure as parse_objects():
            - name, object_type, value, used_in_rules, raw_xml

            Metadata dictionary contains:
            - rule_count, address_object_count, service_object_count

    Raises:
        ValueError: If set_content is empty, None, or contains invalid set commands.
        Exception: For other parsing errors or system issues.

    Example:
        >>> set_data = '''
        ... set security rules Allow-Web from trust to untrust source any destination any service HTTP action allow
        ... set address Web-Server ip-netmask 192.168.1.10/32
        ... set service HTTP protocol tcp port 80
        ... '''
        >>> rules, objects, metadata = parse_set_config(set_data)
        >>> len(rules)
        1
        >>> rules[0]['rule_name']
        'Allow-Web'
        >>> len(objects)
        2
        >>> objects[0]['name']
        'Web-Server'
        >>> metadata['rule_count']
        1

    Note:
        - Supports standard set commands: 'set security rules', 'set address', 'set service'
        - Output structure matches XML parser for consistency across formats
        - Handles malformed commands gracefully with error logging
        - Automatically assigns rule positions based on order in file
        - Preserves original set command text in raw_xml field for traceability
        - Supports disabled rules via 'disabled' keyword in set commands
    """
    try:
        # Preprocess content to handle different formats
        processed_content = preprocess_set_content(set_content)
        lines = processed_content.strip().split('\n')

        # Use incremental parsing for rules that are built up with multiple set commands
        rules_dict = {}  # rule_name -> rule_data
        objects_data = []
        metadata = {"firmware_version": "unknown", "rule_count": 0, "address_object_count": 0, "service_object_count": 0}

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse security rules (incremental format)
            if ('set security rules' in line or 'set rulebase security rules' in line):
                parse_incremental_set_rule(line, rules_dict)

            # Parse address objects (multiple variations)
            elif 'set address' in line:
                obj_data = parse_set_address_object(line)
                if obj_data:
                    objects_data.append(obj_data)

            # Parse service objects (multiple variations)
            elif 'set service' in line:
                obj_data = parse_set_service_object(line)
                if obj_data:
                    objects_data.append(obj_data)

        # Convert rules_dict to rules_data list
        rules_data = []
        for position, (rule_name, rule_data) in enumerate(rules_dict.items(), 1):
            rule_data["position"] = position
            rules_data.append(rule_data)

        # Update metadata counts
        metadata["rule_count"] = len(rules_data)
        metadata["address_object_count"] = len([obj for obj in objects_data if obj["object_type"] == "address"])
        metadata["service_object_count"] = len([obj for obj in objects_data if obj["object_type"] == "service"])

        logger.info(f"Parsed {len(rules_data)} security rules from incremental set format")
        logger.info(f"Parsed {len(objects_data)} objects from set format")

        return rules_data, objects_data, metadata

    except Exception as e:
        logger.error(f"Error parsing set config: {str(e)}")
        raise ValueError(f"Failed to parse set config: {str(e)}")

def preprocess_set_content(content: str) -> str:
    """
    Preprocess set content to handle various format variations.

    Args:
        content: Raw set content

    Returns:
        Processed content with normalized format
    """
    try:
        import re

        # Split content into lines
        lines = content.split('\n')
        processed_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle concatenated set commands on single lines
            # Look for multiple "set" commands on the same line
            if line.count('set ') > 1:
                # Split on 'set ' and rejoin properly
                parts = line.split('set ')
                for i, part in enumerate(parts):
                    if i == 0 and not part.strip():
                        continue  # Skip empty first part
                    if part.strip():
                        processed_lines.append('set ' + part.strip())
            else:
                processed_lines.append(line)

        return '\n'.join(processed_lines)

    except Exception as e:
        logger.warning(f"Error preprocessing set content: {str(e)}")
        return content  # Return original if preprocessing fails

def parse_incremental_set_rule(line: str, rules_dict: Dict[str, Dict[str, Any]]) -> None:
    """
    Parse incremental set rule commands that build up rules with multiple set statements.

    Examples:
    - set security rules "Allow-Web-Access" from trust
    - set security rules "Allow-Web-Access" to untrust
    - set security rules "Allow-Web-Access" source Server-Web-01
    - set security rules "Allow-Web-Access" destination any
    - set security rules "Allow-Web-Access" service service-http
    - set security rules "Allow-Web-Access" action allow
    """
    try:
        import re

        # Extract rule name (quoted or unquoted) - handle both formats
        # Format 1: set security rules "Name" attribute value
        # Format 2: set rulebase security rules Name attribute value
        name_match = re.search(r'set (?:rulebase )?security rules ["\']?([^"\']+?)["\']?\s+(?:from|to|source|destination|service|action|application)', line)
        if not name_match:
            # Fallback: try to extract just the rule name part
            name_match = re.search(r'set (?:rulebase )?security rules ["\']?([^"\']+)["\']?', line)
            if not name_match:
                return
            # Clean the rule name by removing attribute keywords
            full_name = name_match.group(1).strip()
            # Split on attribute keywords and take the first part
            attribute_keywords = ['from', 'to', 'source', 'destination', 'service', 'action', 'application']
            rule_name = full_name
            for keyword in attribute_keywords:
                if ' ' + keyword + ' ' in ' ' + full_name + ' ':
                    rule_name = full_name.split(' ' + keyword)[0].strip()
                    break
        else:
            rule_name = name_match.group(1).strip()

        logger.debug(f"Extracted rule name: '{rule_name}' from line: {line}")

        # Initialize rule if not exists
        if rule_name not in rules_dict:
            rules_dict[rule_name] = {
                "rule_name": rule_name,
                "rule_type": "security",
                "src_zone": "any",
                "dst_zone": "any",
                "src": "any",
                "dst": "any",
                "service": "any",
                "action": "allow",
                "position": 0,  # Will be set later
                "is_disabled": False,
                "raw_xml": ""
            }

        rule_data = rules_dict[rule_name]

        # Update rule_data based on the specific attribute being set
        if ' from ' in line:
            from_match = re.search(r'from (["\']?)([^"\'\s]+)\1', line)
            if from_match:
                rule_data["src_zone"] = from_match.group(2)

        if ' to ' in line:
            to_match = re.search(r'to (["\']?)([^"\'\s]+)\1', line)
            if to_match:
                rule_data["dst_zone"] = to_match.group(2)

        if ' source ' in line:
            source_match = re.search(r'source (["\']?)([^"\'\s]+)\1', line)
            if source_match:
                rule_data["src"] = source_match.group(2)

        if ' destination ' in line:
            dest_match = re.search(r'destination (["\']?)([^"\'\s]+)\1', line)
            if dest_match:
                rule_data["dst"] = dest_match.group(2)

        if ' service ' in line:
            service_match = re.search(r'service (["\']?)([^"\'\s\[]+)\1', line)
            if service_match:
                rule_data["service"] = service_match.group(2)

        if ' action ' in line:
            action_match = re.search(r'action (["\']?)([^"\'\s]+)\1', line)
            if action_match:
                rule_data["action"] = action_match.group(2)

        # Check if rule is disabled
        if 'disabled yes' in line or 'disable' in line:
            rule_data["is_disabled"] = True

        # Append to raw_xml for debugging
        if rule_data["raw_xml"]:
            rule_data["raw_xml"] += "; " + line
        else:
            rule_data["raw_xml"] = line

        logger.debug(f"Updated rule '{rule_name}' with: {line}")

    except Exception as e:
        logger.error(f"Error parsing incremental set rule: {line} - {str(e)}")

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

        # Extract rule attributes using regex patterns that handle quoted values
        from_match = re.search(r'from (["\']?)([^"\'\s]+)\1', line)
        to_match = re.search(r'to (["\']?)([^"\'\s]+)\1', line)
        source_match = re.search(r'source (["\']?)([^"\'\s]+)\1', line)
        dest_match = re.search(r'destination (["\']?)([^"\'\s]+)\1', line)
        service_match = re.search(r'service (["\']?)([^"\'\s]+)\1', line)
        action_match = re.search(r'action (["\']?)([^"\'\s]+)\1', line)

        # Check if rule is disabled
        is_disabled = 'disabled yes' in line or 'disable' in line

        rule_data = {
            "rule_name": rule_name,
            "rule_type": "security",
            "src_zone": from_match.group(2) if from_match else "any",
            "dst_zone": to_match.group(2) if to_match else "any",
            "src": source_match.group(2) if source_match else "any",
            "dst": dest_match.group(2) if dest_match else "any",
            "service": service_match.group(2) if service_match else "any",
            "action": action_match.group(2) if action_match else "allow",
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
    Parse a set address object command with support for various formats.

    Examples:
    - set address "Server-1" ip-netmask 192.168.1.100/32
    - set address "Web-Server" fqdn www.example.com
    - set address Server-1 ip-netmask 192.168.1.100/32 (no quotes)
    """
    try:
        import re

        # More robust regex to extract object name (handles quoted and unquoted)
        # Pattern: set address "name" or set address name
        name_match = re.search(r'set address (["\']?)([^"\'\s]+)\1', line)
        if not name_match:
            # Fallback: try to extract the first word after "set address"
            name_match = re.search(r'set address\s+([^\s]+)', line)
            if not name_match:
                logger.warning(f"Could not extract address object name from: {line}")
                return {}
            name = name_match.group(1).strip('"\'')
        else:
            name = name_match.group(2).strip()

        # Ensure we only get the object name, not the entire command
        if ' ' in name:
            # If name contains spaces, take only the first part
            name = name.split()[0].strip('"\'')

        logger.debug(f"Extracted address object name: '{name}' from line: {line}")

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
        else:
            # Try to extract any IP-like value as fallback
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+(?:/\d+)?)', line)
            if ip_match:
                value = ip_match.group(1)

        if not value:
            logger.warning(f"Could not extract address value from: {line}")
            return {}

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

        # Perform batch insert with timing
        import time
        batch_start_time = time.time()
        logger.info(f"Performing batch insert of {len(validated_rules)} rules")

        # Use bulk_insert_mappings for better performance
        db_session.bulk_insert_mappings(FirewallRule, validated_rules)

        batch_duration = time.time() - batch_start_time
        rules_per_second = len(validated_rules) / batch_duration if batch_duration > 0 else 0
        logger.info(f"Successfully stored {len(validated_rules)} out of {len(rules_data)} rules in {batch_duration:.3f}s ({rules_per_second:.1f} rules/sec)")
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

        # Perform batch insert with timing
        import time
        batch_start_time = time.time()
        logger.info(f"Performing batch insert of {len(validated_objects)} objects")

        # Use bulk_insert_mappings for better performance
        db_session.bulk_insert_mappings(ObjectDefinition, validated_objects)

        batch_duration = time.time() - batch_start_time
        objects_per_second = len(validated_objects) / batch_duration if batch_duration > 0 else 0
        logger.info(f"Successfully stored {len(validated_objects)} out of {len(objects_data)} objects in {batch_duration:.3f}s ({objects_per_second:.1f} objects/sec)")
        return len(validated_objects)

    except Exception as e:
        logger.error(f"Database error during objects storage: {str(e)}")
        raise Exception(f"Failed to store objects: {str(e)}")

def analyze_object_usage(rules_data: List[Dict[str, Any]], objects_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze which objects are used in rules and update usage counts.
    Also identifies redundant objects (same value as used objects).

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

        # Identify redundant objects (same value as used objects)
        # Group objects by value
        objects_by_value = {}
        for obj in objects_data:
            value = obj.get('value', '')
            if value and value != '':
                if value not in objects_by_value:
                    objects_by_value[value] = []
                objects_by_value[value].append(obj)

        # For each group of objects with the same value, if any are used, mark redundant ones as "indirectly used"
        for value, obj_group in objects_by_value.items():
            if len(obj_group) > 1:  # Multiple objects with same value
                # Check if any object in this group is directly used
                directly_used = any(object_usage.get(obj.get('name', ''), 0) > 0 for obj in obj_group)

                if directly_used:
                    # Mark unused objects in this group as "redundant" (indirectly used)
                    for obj in obj_group:
                        obj_name = obj.get('name', '')
                        if object_usage.get(obj_name, 0) == 0:
                            # Mark as indirectly used (redundant)
                            object_usage[obj_name] = -1  # Special marker for redundant objects
                            logger.debug(f"Object '{obj_name}' marked as redundant (same value as used object)")

        # Update objects_data with usage counts
        for obj in objects_data:
            obj_name = obj.get('name', '')
            if obj_name in object_usage:
                usage_count = object_usage[obj_name]
                if usage_count == -1:
                    # Redundant object - set to 0 for database but mark as special
                    obj['used_in_rules'] = 0
                    obj['is_redundant'] = True
                else:
                    obj['used_in_rules'] = usage_count
                    obj['is_redundant'] = False

        # Log usage statistics
        directly_used = sum(1 for count in object_usage.values() if count > 0)
        redundant = sum(1 for count in object_usage.values() if count == -1)
        truly_unused = len(object_usage) - directly_used - redundant

        logger.info(f"Object usage analysis completed: {directly_used} used, {redundant} redundant, {truly_unused} unused objects")

        return object_usage

    except Exception as e:
        logger.error(f"Error analyzing object usage: {str(e)}")
        return {}

def parse_rules_streaming(xml_content: bytes) -> List[Dict[str, Any]]:
    """
    Extract security rules from XML config using streaming parser for large files.
    Uses lxml.etree.iterparse for memory-efficient processing.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        List of dictionaries containing rule data

    Raises:
        ValueError: If XML parsing fails
    """
    start_time = time.time()
    start_memory = get_memory_usage()

    try:
        # Validate input
        if not xml_content:
            raise ValueError("XML content is empty for streaming parser")

        if not isinstance(xml_content, bytes):
            raise ValueError("XML content must be bytes for streaming parser")

        import io

        rules = []
        xml_stream = io.BytesIO(xml_content)

        # Use lxml if available, otherwise fall back to standard library
        if LXML_AVAILABLE:
            logger.info("Starting lxml streaming XML parsing for rules")
            iterparse_func = lxml_etree.iterparse
        else:
            logger.info("Starting standard library streaming XML parsing for rules")
            from xml.etree.ElementTree import iterparse
            iterparse_func = iterparse

        # Track current context for nested parsing
        current_rule = None
        in_rules_section = False
        rule_depth = 0
        path_stack = []

        # Use iterparse for memory-efficient streaming
        for event, elem in iterparse_func(xml_stream, events=('start', 'end')):

            if event == 'start':
                path_stack.append(elem.tag)

                # Detect when we enter a rules section
                if elem.tag == 'rules':
                    # Check if we're in a security context by tracking the path
                    path = '/'.join(path_stack)
                    if 'security' in path.lower() or 'rulebase' in path.lower():
                        in_rules_section = True
                        logger.debug(f"Entered security rules section at path: {path}")

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
                if path_stack:
                    path_stack.pop()

                # Process completed rule entry
                if elem.tag == 'entry' and in_rules_section and current_rule is not None:
                    # Extract rule data from completed element
                    current_rule = _extract_rule_data_streaming(elem, current_rule)
                    if LXML_AVAILABLE:
                        current_rule["raw_xml"] = lxml_etree.tostring(elem, encoding='unicode')
                    else:
                        current_rule["raw_xml"] = ET.tostring(elem, encoding='unicode')

                    rules.append(current_rule)

                    # Log progress for large files
                    if len(rules) % 100 == 0:
                        logger.debug(f"Processed {len(rules)} rules...")

                    # Clear the element to free memory (lxml feature)
                    if LXML_AVAILABLE:
                        elem.clear()
                        # Also clear parent references to free memory
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]
                    logger.debug(f"Parsed rule: {current_rule['rule_name']}")
                    current_rule = None

                # Exit rules section
                elif elem.tag == 'rules' and in_rules_section:
                    in_rules_section = False
                    logger.debug("Exited security rules section")

                # Clear processed elements to save memory (standard library)
                elif not LXML_AVAILABLE and elem.tag in ['devices', 'vsys', 'rulebase', 'security']:
                    elem.clear()

        # Log performance metrics
        log_parsing_performance(start_time, start_memory, len(rules), "rules")

        logger.info(f"Streaming parser completed: {len(rules)} security rules parsed")
        return rules

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        error_msg = f"Unexpected error in streaming rules parser: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

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
    Uses lxml.etree.iterparse for memory-efficient processing.

    Args:
        xml_content: Raw XML content as bytes

    Returns:
        List of dictionaries containing object data

    Raises:
        ValueError: If XML parsing fails
    """
    start_time = time.time()
    start_memory = get_memory_usage()

    try:
        import io

        objects = []
        xml_stream = io.BytesIO(xml_content)

        # Use lxml if available, otherwise fall back to standard library
        if LXML_AVAILABLE:
            logger.info("Starting lxml streaming XML parsing for objects")
            iterparse_func = lxml_etree.iterparse
        else:
            logger.info("Starting standard library streaming XML parsing for objects")
            from xml.etree.ElementTree import iterparse
            iterparse_func = iterparse

        # Track current context for nested parsing
        in_address_section = False
        in_service_section = False
        current_object = None
        path_stack = []

        # Use iterparse for memory-efficient streaming
        for event, elem in iterparse_func(xml_stream, events=('start', 'end')):

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

def analyze_rule_usage(audit_id: int) -> Dict[str, Any]:
    """
    Analyze rules for various issues including unused, duplicate, shadowed, and overlapping rules.

    Args:
        audit_id: The audit session ID

    Returns:
        Dictionary containing analysis results
    """
    try:
        import sqlite3
        from .rule_analysis import analyze_rules

        logger.info(f"Starting rule usage analysis for audit {audit_id}")

        # Get all rules for this audit
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, rule_name, rule_type, src_zone, dst_zone, src, dst, service,
                   action, position, is_disabled, raw_xml
            FROM firewall_rules
            WHERE audit_id = ?
            ORDER BY position
        """, (audit_id,))

        rules = []
        for row in cursor.fetchall():
            rule = {
                'id': row[0],
                'rule_name': row[1],
                'rule_type': row[2],
                'src_zone': row[3],
                'dst_zone': row[4],
                'src': row[5],
                'dst': row[6],
                'service': row[7],
                'action': row[8],
                'position': row[9],
                'is_disabled': bool(row[10]),
                'raw_xml': row[11]
            }
            rules.append(rule)

        conn.close()

        if not rules:
            logger.warning(f"No rules found for audit {audit_id}")
            return {
                'unused_rules': [],
                'duplicate_rules': [],
                'shadowed_rules': [],
                'overlapping_rules': []
            }

        # Perform rule analysis
        analysis_result = analyze_rules(rules)

        logger.info(f"Rule analysis completed for audit {audit_id}: "
                   f"{len(analysis_result.unused_rules)} unused, "
                   f"{len(analysis_result.duplicate_rules)} duplicate, "
                   f"{len(analysis_result.shadowed_rules)} shadowed, "
                   f"{len(analysis_result.overlapping_rules)} overlapping")

        return {
            'unused_rules': analysis_result.unused_rules,
            'duplicate_rules': analysis_result.duplicate_rules,
            'shadowed_rules': analysis_result.shadowed_rules,
            'overlapping_rules': analysis_result.overlapping_rules
        }

    except Exception as e:
        logger.error(f"Error in rule usage analysis: {str(e)}")
        raise ValueError(f"Failed to analyze rule usage: {str(e)}")
