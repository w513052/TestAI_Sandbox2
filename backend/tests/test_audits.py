#!/usr/bin/env python3
"""
Unit tests for the file upload endpoint (POST /api/v1/audits).
Task 14: Write Unit Tests for File Upload
"""

import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db, Base
from src.models import AuditSession, FirewallRule, ObjectDefinition

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_firewall_tool.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def reset_database():
    """Reset the database before each test."""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test
    Base.metadata.drop_all(bind=engine)

def create_valid_xml_content():
    """Create a valid XML configuration file for testing."""
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<config version="10.1.0">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <address>
            <entry name="Server-001">
              <ip-netmask>192.168.1.10/32</ip-netmask>
            </entry>
            <entry name="Server-002">
              <ip-netmask>192.168.1.20/32</ip-netmask>
            </entry>
            <entry name="Database-Server">
              <ip-netmask>192.168.2.10/32</ip-netmask>
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
                  <source><member>Server-001</member></source>
                  <destination><member>any</member></destination>
                  <service><member>HTTP-Service</member></service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-HTTPS-Traffic">
                  <from><member>trust</member></from>
                  <to><member>untrust</member></to>
                  <source><member>Server-002</member></source>
                  <destination><member>any</member></destination>
                  <service><member>HTTPS-Service</member></service>
                  <action>allow</action>
                </entry>
                <entry name="Allow-DB-Access">
                  <from><member>trust</member></from>
                  <to><member>dmz</member></to>
                  <source><member>any</member></source>
                  <destination><member>Database-Server</member></destination>
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

def create_valid_set_content():
    """Create a valid SET configuration file for testing."""
    return '''set security rules Allow-Web-Traffic from trust to untrust source Server-001 destination any service HTTP-Service action allow
set security rules Allow-HTTPS-Traffic from trust to untrust source Server-002 destination any service HTTPS-Service action allow
set security rules Allow-DB-Access from trust to dmz source any destination Database-Server service any action allow
set address Server-001 ip-netmask 192.168.1.10/32
set address Server-002 ip-netmask 192.168.1.20/32
set address Database-Server ip-netmask 192.168.2.10/32
set service HTTP-Service protocol tcp port 80
set service HTTPS-Service protocol tcp port 443'''.encode('utf-8')

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
            <!-- Missing closing tags -->
          </address>
        </entry>
      </vsys>
    </entry>
  </devices>
<!-- Missing closing config tag -->'''

class TestFileUpload:
    """Test cases for file upload endpoint."""

    def test_successful_xml_file_upload(self, reset_database):
        """Test successful upload of a valid XML file."""
        xml_content = create_valid_xml_content()
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("test_config.xml", xml_content, "application/xml")},
            data={"session_name": "Test_XML_Upload"}
        )
        
        assert response.status_code == 200
        
        response_data = response.json()
        
        # Verify response structure
        assert response_data["status"] == "success"
        assert response_data["message"] == "Audit session created successfully"
        assert "data" in response_data
        
        data = response_data["data"]
        
        # Verify required fields
        assert "audit_id" in data
        assert isinstance(data["audit_id"], int)
        assert data["audit_id"] > 0
        
        assert data["session_name"] == "Test_XML_Upload"
        assert data["filename"] == "test_config.xml"
        assert data["file_type"] == "XML"
        assert "file_hash" in data
        assert "start_time" in data
        assert "metadata" in data
        
        # Verify metadata contains expected fields
        metadata = data["metadata"]
        assert "rules_parsed" in metadata
        assert "objects_parsed" in metadata
        assert metadata["rules_parsed"] >= 3  # Should have at least 3 rules
        assert metadata["objects_parsed"] >= 2  # Should have at least 2 objects

    def test_successful_set_file_upload(self, reset_database):
        """Test successful upload of a valid SET file."""
        set_content = create_valid_set_content()
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("test_config.txt", set_content, "text/plain")},
            data={"session_name": "Test_SET_Upload"}
        )
        
        assert response.status_code == 200
        
        response_data = response.json()
        
        # Verify response structure
        assert response_data["status"] == "success"
        assert response_data["message"] == "Audit session created successfully"
        
        data = response_data["data"]
        assert isinstance(data["audit_id"], int)
        assert data["session_name"] == "Test_SET_Upload"
        assert data["filename"] == "test_config.txt"
        assert data["file_type"] == "SET"

    def test_auto_generated_session_name(self, reset_database):
        """Test upload without session name generates automatic name."""
        xml_content = create_valid_xml_content()
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("test_config.xml", xml_content, "application/xml")}
        )
        
        assert response.status_code == 200
        
        response_data = response.json()
        data = response_data["data"]
        
        # Should have auto-generated session name
        assert "session_name" in data
        assert data["session_name"].startswith("Audit_")
        assert len(data["session_name"]) > 10  # Should include timestamp

    def test_invalid_file_type_upload(self, reset_database):
        """Test upload of invalid file type returns 400 error."""
        pdf_content = b"%PDF-1.4 fake pdf content"
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("document.pdf", pdf_content, "application/pdf")},
            data={"session_name": "Test_Invalid_Upload"}
        )
        
        assert response.status_code == 400
        
        response_data = response.json()
        assert "detail" in response_data
        assert "error_code" in response_data["detail"]
        assert response_data["detail"]["error_code"] == "INVALID_FILE_TYPE"

    def test_empty_file_upload(self, reset_database):
        """Test upload of empty file returns 400 error."""
        empty_content = b""
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("empty.xml", empty_content, "application/xml")},
            data={"session_name": "Test_Empty_Upload"}
        )
        
        assert response.status_code == 400
        
        response_data = response.json()
        assert "detail" in response_data
        assert "error_code" in response_data["detail"]
        assert response_data["detail"]["error_code"] == "EMPTY_FILE"

    def test_malformed_xml_upload(self, reset_database):
        """Test upload of malformed XML returns 400 error."""
        malformed_content = create_malformed_xml_content()
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("malformed.xml", malformed_content, "application/xml")},
            data={"session_name": "Test_Malformed_Upload"}
        )
        
        assert response.status_code == 400
        
        response_data = response.json()
        assert "detail" in response_data
        assert "error_code" in response_data["detail"]
        assert response_data["detail"]["error_code"] == "INVALID_CONFIG_FILE"

    def test_missing_file_upload(self, reset_database):
        """Test upload without file returns 422 error."""
        response = client.post(
            "/api/v1/audits/",
            data={"session_name": "Test_Missing_File"}
        )
        
        assert response.status_code == 422  # FastAPI validation error

    def test_database_persistence(self, reset_database):
        """Test that uploaded data is properly stored in database."""
        xml_content = create_valid_xml_content()
        
        response = client.post(
            "/api/v1/audits/",
            files={"file": ("test_persistence.xml", xml_content, "application/xml")},
            data={"session_name": "Test_DB_Persistence"}
        )
        
        assert response.status_code == 200
        
        response_data = response.json()
        audit_id = response_data["data"]["audit_id"]
        
        # Verify data was stored in database
        db = TestingSessionLocal()
        try:
            # Check audit session was created
            audit_session = db.query(AuditSession).filter(AuditSession.id == audit_id).first()
            assert audit_session is not None
            assert audit_session.session_name == "Test_DB_Persistence"
            assert audit_session.filename == "test_persistence.xml"
            
            # Check rules were stored
            rules = db.query(FirewallRule).filter(FirewallRule.audit_id == audit_id).all()
            assert len(rules) >= 3  # Should have at least 3 rules
            
            # Check objects were stored
            objects = db.query(ObjectDefinition).filter(ObjectDefinition.audit_id == audit_id).all()
            assert len(objects) >= 2  # Should have at least 2 objects
            
        finally:
            db.close()

    def test_file_hash_generation(self, reset_database):
        """Test that file hash is properly generated and consistent."""
        xml_content = create_valid_xml_content()
        
        # Upload same file twice
        response1 = client.post(
            "/api/v1/audits/",
            files={"file": ("test_hash1.xml", xml_content, "application/xml")},
            data={"session_name": "Test_Hash_1"}
        )
        
        response2 = client.post(
            "/api/v1/audits/",
            files={"file": ("test_hash2.xml", xml_content, "application/xml")},
            data={"session_name": "Test_Hash_2"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        hash1 = response1.json()["data"]["file_hash"]
        hash2 = response2.json()["data"]["file_hash"]
        
        # Same content should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hash length

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
