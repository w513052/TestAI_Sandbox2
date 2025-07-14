#!/usr/bin/env python3
"""
Unit tests for parsing function documentation.
Task 20: Document Parsing Functions
"""

import pytest
import inspect
import logging
from src.utils.parse_config import parse_rules, parse_objects, parse_metadata, parse_set_config

# Configure logging for test traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestDocumentation:
    """Test cases for parsing function documentation compliance."""

    def test_parse_rules_docstring_compliance(self):
        """Test that parse_rules has comprehensive Google-style docstring."""
        logger.info("Testing parse_rules docstring compliance")
        
        docstring = parse_rules.__doc__
        
        # Verify docstring exists
        assert docstring is not None, "parse_rules should have a docstring"
        assert len(docstring.strip()) > 100, "Docstring should be comprehensive"
        
        # Check for required sections
        required_sections = ["Args:", "Returns:", "Raises:", "Example:", "Note:"]
        for section in required_sections:
            assert section in docstring, f"Docstring should contain '{section}' section"
        
        # Check for specific content
        assert "xml_content (bytes)" in docstring, "Should document xml_content parameter type"
        assert "List[Dict[str, Any]]" in docstring, "Should document return type"
        assert "ValueError" in docstring, "Should document ValueError exception"
        assert "rule_name" in docstring, "Should document rule_name field"
        assert "action" in docstring, "Should document action field"
        assert "position" in docstring, "Should document position field"
        
        # Check for examples
        assert ">>>" in docstring, "Should contain usage examples"
        assert "xml_data" in docstring, "Should contain example variable"
        
        logger.info("parse_rules docstring compliance test passed")

    def test_parse_objects_docstring_compliance(self):
        """Test that parse_objects has comprehensive Google-style docstring."""
        logger.info("Testing parse_objects docstring compliance")
        
        docstring = parse_objects.__doc__
        
        # Verify docstring exists
        assert docstring is not None, "parse_objects should have a docstring"
        assert len(docstring.strip()) > 100, "Docstring should be comprehensive"
        
        # Check for required sections
        required_sections = ["Args:", "Returns:", "Raises:", "Example:", "Note:"]
        for section in required_sections:
            assert section in docstring, f"Docstring should contain '{section}' section"
        
        # Check for specific content
        assert "xml_content (bytes)" in docstring, "Should document xml_content parameter type"
        assert "List[Dict[str, Any]]" in docstring, "Should document return type"
        assert "ValueError" in docstring, "Should document ValueError exception"
        assert "object_type" in docstring, "Should document object_type field"
        assert "address" in docstring, "Should mention address objects"
        assert "service" in docstring, "Should mention service objects"
        
        # Check for examples
        assert ">>>" in docstring, "Should contain usage examples"
        assert "Web-Server" in docstring, "Should contain example object name"
        
        logger.info("parse_objects docstring compliance test passed")

    def test_parse_metadata_docstring_compliance(self):
        """Test that parse_metadata has comprehensive Google-style docstring."""
        logger.info("Testing parse_metadata docstring compliance")
        
        docstring = parse_metadata.__doc__
        
        # Verify docstring exists
        assert docstring is not None, "parse_metadata should have a docstring"
        assert len(docstring.strip()) > 100, "Docstring should be comprehensive"
        
        # Check for required sections
        required_sections = ["Args:", "Returns:", "Raises:", "Example:", "Note:"]
        for section in required_sections:
            assert section in docstring, f"Docstring should contain '{section}' section"
        
        # Check for specific content
        assert "xml_content (bytes)" in docstring, "Should document xml_content parameter type"
        assert "Dict[str, Any]" in docstring, "Should document return type"
        assert "ValueError" in docstring, "Should document ValueError exception"
        assert "firmware_version" in docstring, "Should document firmware_version field"
        assert "rule_count" in docstring, "Should document rule_count field"
        assert "address_object_count" in docstring, "Should document address_object_count field"
        
        # Check for examples
        assert ">>>" in docstring, "Should contain usage examples"
        assert "metadata[" in docstring, "Should contain example usage"
        
        logger.info("parse_metadata docstring compliance test passed")

    def test_parse_set_config_docstring_compliance(self):
        """Test that parse_set_config has comprehensive Google-style docstring."""
        logger.info("Testing parse_set_config docstring compliance")
        
        docstring = parse_set_config.__doc__
        
        # Verify docstring exists
        assert docstring is not None, "parse_set_config should have a docstring"
        assert len(docstring.strip()) > 100, "Docstring should be comprehensive"
        
        # Check for required sections
        required_sections = ["Args:", "Returns:", "Raises:", "Example:", "Note:"]
        for section in required_sections:
            assert section in docstring, f"Docstring should contain '{section}' section"
        
        # Check for specific content
        assert "set_content (str)" in docstring, "Should document set_content parameter type"
        assert "tuple[" in docstring, "Should document tuple return type"
        assert "ValueError" in docstring, "Should document ValueError exception"
        assert "set security rules" in docstring, "Should mention set commands"
        assert "CLI format" in docstring, "Should mention CLI format"
        
        # Check for examples
        assert ">>>" in docstring, "Should contain usage examples"
        assert "set_data" in docstring, "Should contain example variable"
        assert "rules, objects, metadata" in docstring, "Should show tuple unpacking"
        
        logger.info("parse_set_config docstring compliance test passed")

    def test_function_signatures_documented(self):
        """Test that all function signatures match their documentation."""
        logger.info("Testing function signatures match documentation")
        
        # Test parse_rules signature
        sig = inspect.signature(parse_rules)
        params = list(sig.parameters.keys())
        assert "xml_content" in params, "parse_rules should have xml_content parameter"
        assert sig.parameters["xml_content"].annotation == bytes, "xml_content should be annotated as bytes"
        
        # Test parse_objects signature
        sig = inspect.signature(parse_objects)
        params = list(sig.parameters.keys())
        assert "xml_content" in params, "parse_objects should have xml_content parameter"
        assert sig.parameters["xml_content"].annotation == bytes, "xml_content should be annotated as bytes"
        
        # Test parse_metadata signature
        sig = inspect.signature(parse_metadata)
        params = list(sig.parameters.keys())
        assert "xml_content" in params, "parse_metadata should have xml_content parameter"
        assert sig.parameters["xml_content"].annotation == bytes, "xml_content should be annotated as bytes"
        
        # Test parse_set_config signature
        sig = inspect.signature(parse_set_config)
        params = list(sig.parameters.keys())
        assert "set_content" in params, "parse_set_config should have set_content parameter"
        assert sig.parameters["set_content"].annotation == str, "set_content should be annotated as str"
        
        logger.info("Function signatures documentation test passed")

    def test_docstring_examples_syntax(self):
        """Test that docstring examples have valid Python syntax."""
        logger.info("Testing docstring examples syntax")
        
        functions_to_test = [parse_rules, parse_objects, parse_metadata, parse_set_config]
        
        for func in functions_to_test:
            docstring = func.__doc__
            assert docstring is not None, f"{func.__name__} should have docstring"
            
            # Extract example code blocks
            lines = docstring.split('\n')
            in_example = False
            example_lines = []
            
            for line in lines:
                if ">>>" in line:
                    in_example = True
                    # Extract the code after >>>
                    code_line = line.split(">>>", 1)[1].strip()
                    if code_line:
                        example_lines.append(code_line)
                elif in_example and line.strip().startswith("..."):
                    # Continuation line
                    code_line = line.split("...", 1)[1].strip()
                    if code_line:
                        example_lines.append(code_line)
                elif in_example and not line.strip():
                    # Empty line continues example
                    continue
                elif in_example:
                    # End of example block
                    in_example = False
            
            # Verify we found examples
            assert len(example_lines) > 0, f"{func.__name__} should have code examples in docstring"
            
            # Test that example code is syntactically valid
            example_code = '\n'.join(example_lines)
            try:
                compile(example_code, f"<{func.__name__}_docstring>", "exec")
                logger.info(f"{func.__name__} docstring examples have valid syntax")
            except SyntaxError as e:
                pytest.fail(f"{func.__name__} docstring examples have syntax error: {e}")

    def test_docstring_references_dbschema(self):
        """Test that docstrings reference DBSchema.txt data structures."""
        logger.info("Testing docstring references to DBSchema.txt")
        
        # Test parse_rules references
        rules_docstring = parse_rules.__doc__
        assert "rule_name" in rules_docstring, "Should reference rule_name from DBSchema"
        assert "src_zone" in rules_docstring, "Should reference src_zone from DBSchema"
        assert "dst_zone" in rules_docstring, "Should reference dst_zone from DBSchema"
        assert "is_disabled" in rules_docstring, "Should reference is_disabled from DBSchema"
        
        # Test parse_objects references
        objects_docstring = parse_objects.__doc__
        assert "object_type" in objects_docstring, "Should reference object_type from DBSchema"
        assert "used_in_rules" in objects_docstring, "Should reference used_in_rules from DBSchema"
        
        # Test parse_metadata references
        metadata_docstring = parse_metadata.__doc__
        assert "firmware_version" in metadata_docstring, "Should reference firmware_version from DBSchema"
        assert "rule_count" in metadata_docstring, "Should reference rule_count from DBSchema"
        assert "address_object_count" in metadata_docstring, "Should reference address_object_count from DBSchema"
        assert "service_object_count" in metadata_docstring, "Should reference service_object_count from DBSchema"
        
        logger.info("DBSchema.txt references test passed")

    def test_google_style_guide_compliance(self):
        """Test that docstrings follow Google Python Style Guide format."""
        logger.info("Testing Google Python Style Guide compliance")
        
        functions_to_test = [parse_rules, parse_objects, parse_metadata, parse_set_config]
        
        for func in functions_to_test:
            docstring = func.__doc__
            assert docstring is not None, f"{func.__name__} should have docstring"
            
            # Check for proper section formatting
            assert "Args:" in docstring, f"{func.__name__} should have Args: section"
            assert "Returns:" in docstring, f"{func.__name__} should have Returns: section"
            assert "Raises:" in docstring, f"{func.__name__} should have Raises: section"
            
            # Check for proper parameter documentation format
            lines = docstring.split('\n')
            args_section_found = False
            
            for line in lines:
                if "Args:" in line:
                    args_section_found = True
                elif args_section_found and "(" in line and ")" in line:
                    # Should have parameter with type annotation
                    assert ":" in line, f"{func.__name__} parameters should have descriptions"
                elif args_section_found and line.strip() and not line.startswith(' '):
                    # End of Args section
                    break
            
            logger.info(f"{func.__name__} follows Google Style Guide format")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
