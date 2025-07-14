#!/usr/bin/env python3
"""
Unit tests for database write optimization with large rule sets.
Task 19: Optimize Database Writes for Large Rule Sets
"""

import pytest
import logging
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import AuditSession, FirewallRule, ObjectDefinition
from src.utils.parse_config import store_rules, store_objects

# Configure logging for performance monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database_optimization.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def reset_test_database():
    """Reset the test database before each test."""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(reset_test_database):
    """Provide a database session for testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def sample_audit_session(db_session):
    """Create a sample audit session for testing."""
    audit_session = AuditSession(
        session_name="Test_Database_Optimization",
        filename="test_large_config.xml",
        file_hash="test_hash_optimization",
        start_time=datetime.utcnow(),
        config_metadata={"test": "large_dataset"}
    )
    db_session.add(audit_session)
    db_session.commit()
    db_session.refresh(audit_session)
    return audit_session

def create_large_rules_dataset(count=1000):
    """Create a large dataset of rules for performance testing."""
    rules = []
    for i in range(count):
        rule = {
            "rule_name": f"Large-Rule-{i+1:04d}",
            "rule_type": "security",
            "src_zone": "trust" if i % 3 == 0 else ("dmz" if i % 3 == 1 else "untrust"),
            "dst_zone": "untrust" if i % 2 == 0 else "trust",
            "src": f"Server-Group-{(i % 50) + 1}",
            "dst": "any" if i % 4 == 0 else f"Target-Group-{(i % 30) + 1}",
            "service": f"Service-{(i % 20) + 1}" if i % 3 != 0 else "any",
            "action": "allow" if i % 10 != 9 else "deny",
            "position": i + 1,
            "is_disabled": i % 25 == 24,  # Every 25th rule is disabled
            "raw_xml": f"<entry name='Large-Rule-{i+1:04d}'><action>{'allow' if i % 10 != 9 else 'deny'}</action><position>{i+1}</position></entry>"
        }
        rules.append(rule)
    return rules

def create_large_objects_dataset(count=500):
    """Create a large dataset of objects for performance testing."""
    objects = []
    for i in range(count):
        if i % 3 == 0:  # Address objects
            obj = {
                "name": f"Address-Object-{i+1:04d}",
                "object_type": "address",
                "value": f"192.168.{(i % 254) + 1}.{((i * 2) % 254) + 1}/32",
                "used_in_rules": i % 10,
                "raw_xml": f"<entry name='Address-Object-{i+1:04d}'><ip-netmask>192.168.{(i % 254) + 1}.{((i * 2) % 254) + 1}/32</ip-netmask></entry>"
            }
        elif i % 3 == 1:  # Service objects
            port = 8000 + (i % 1000)
            obj = {
                "name": f"Service-Object-{i+1:04d}",
                "object_type": "service",
                "value": f"tcp/{port}",
                "used_in_rules": i % 5,
                "raw_xml": f"<entry name='Service-Object-{i+1:04d}'><protocol><tcp><port>{port}</port></tcp></protocol></entry>"
            }
        else:  # Application objects
            obj = {
                "name": f"Application-Object-{i+1:04d}",
                "object_type": "application",
                "value": f"custom-app-{i+1}",
                "used_in_rules": i % 3,
                "raw_xml": f"<entry name='Application-Object-{i+1:04d}'><category>custom</category></entry>"
            }
        objects.append(obj)
    return objects

class TestDatabaseOptimization:
    """Test cases for database write optimization with large rule sets."""

    def test_large_rules_performance_1000(self, db_session, sample_audit_session):
        """Test storing 1000+ rules with performance monitoring."""
        logger.info("Testing large rules performance with 1000 rules")
        
        # Create large dataset
        large_rules = create_large_rules_dataset(1000)
        audit_id = sample_audit_session.id
        
        # Measure performance
        start_time = time.time()
        logger.info(f"Starting batch insert of {len(large_rules)} rules at {datetime.now()}")
        
        stored_count = store_rules(db_session, audit_id, large_rules)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Batch insert completed in {duration:.3f} seconds")
        logger.info(f"Performance: {stored_count / duration:.1f} rules/second")
        
        # Verify performance requirement (under 5 seconds)
        assert duration < 5.0, f"Database writes took {duration:.3f} seconds, should be under 5 seconds"
        
        # Verify all rules were stored
        assert stored_count == 1000, f"Expected 1000 rules stored, got {stored_count}"
        
        # Verify data integrity
        stored_rules = db_session.query(FirewallRule).filter(FirewallRule.audit_id == audit_id).all()
        assert len(stored_rules) == 1000, f"Expected 1000 rules in database, found {len(stored_rules)}"
        
        # Verify rule data integrity
        for i, rule in enumerate(stored_rules[:10]):  # Check first 10 rules
            assert rule.audit_id == audit_id, f"Rule {i} has wrong audit_id"
            assert rule.rule_name.startswith("Large-Rule-"), f"Rule {i} has wrong name: {rule.rule_name}"
            assert rule.position > 0, f"Rule {i} has invalid position: {rule.position}"
        
        logger.info(f"Successfully stored and verified {stored_count} rules in {duration:.3f} seconds")

    def test_large_objects_performance_500(self, db_session, sample_audit_session):
        """Test storing 500+ objects with performance monitoring."""
        logger.info("Testing large objects performance with 500 objects")
        
        # Create large dataset
        large_objects = create_large_objects_dataset(500)
        audit_id = sample_audit_session.id
        
        # Measure performance
        start_time = time.time()
        logger.info(f"Starting batch insert of {len(large_objects)} objects at {datetime.now()}")
        
        stored_count = store_objects(db_session, audit_id, large_objects)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Batch insert completed in {duration:.3f} seconds")
        logger.info(f"Performance: {stored_count / duration:.1f} objects/second")
        
        # Verify performance (should be reasonable)
        assert duration < 3.0, f"Object storage took {duration:.3f} seconds, should be under 3 seconds"
        
        # Verify all objects were stored
        assert stored_count == 500, f"Expected 500 objects stored, got {stored_count}"
        
        # Verify data integrity
        stored_objects = db_session.query(ObjectDefinition).filter(ObjectDefinition.audit_id == audit_id).all()
        assert len(stored_objects) == 500, f"Expected 500 objects in database, found {len(stored_objects)}"
        
        # Verify object type distribution
        address_objects = [obj for obj in stored_objects if obj.object_type == "address"]
        service_objects = [obj for obj in stored_objects if obj.object_type == "service"]
        application_objects = [obj for obj in stored_objects if obj.object_type == "application"]
        
        logger.info(f"Object distribution: {len(address_objects)} address, {len(service_objects)} service, {len(application_objects)} application")
        
        assert len(address_objects) > 150, "Should have significant number of address objects"
        assert len(service_objects) > 150, "Should have significant number of service objects"
        assert len(application_objects) > 150, "Should have significant number of application objects"
        
        logger.info(f"Successfully stored and verified {stored_count} objects in {duration:.3f} seconds")

    def test_combined_large_dataset_performance(self, db_session, sample_audit_session):
        """Test storing combined large dataset (1500 rules + 750 objects)."""
        logger.info("Testing combined large dataset performance")
        
        # Create large datasets
        large_rules = create_large_rules_dataset(1500)
        large_objects = create_large_objects_dataset(750)
        audit_id = sample_audit_session.id
        
        # Measure combined performance
        total_start_time = time.time()
        
        # Store rules
        rules_start_time = time.time()
        logger.info(f"Starting batch insert of {len(large_rules)} rules")
        rules_stored = store_rules(db_session, audit_id, large_rules)
        rules_duration = time.time() - rules_start_time
        
        # Store objects
        objects_start_time = time.time()
        logger.info(f"Starting batch insert of {len(large_objects)} objects")
        objects_stored = store_objects(db_session, audit_id, large_objects)
        objects_duration = time.time() - objects_start_time
        
        total_duration = time.time() - total_start_time
        
        # Log performance metrics
        logger.info(f"Rules storage: {rules_stored} rules in {rules_duration:.3f}s ({rules_stored/rules_duration:.1f} rules/sec)")
        logger.info(f"Objects storage: {objects_stored} objects in {objects_duration:.3f}s ({objects_stored/objects_duration:.1f} objects/sec)")
        logger.info(f"Total storage: {rules_stored + objects_stored} items in {total_duration:.3f}s")
        
        # Verify performance requirements
        assert rules_duration < 5.0, f"Rules storage took {rules_duration:.3f}s, should be under 5s"
        assert objects_duration < 3.0, f"Objects storage took {objects_duration:.3f}s, should be under 3s"
        assert total_duration < 8.0, f"Total storage took {total_duration:.3f}s, should be under 8s"
        
        # Verify data integrity
        assert rules_stored == 1500, f"Expected 1500 rules stored, got {rules_stored}"
        assert objects_stored == 750, f"Expected 750 objects stored, got {objects_stored}"
        
        # Verify database contents
        stored_rules = db_session.query(FirewallRule).filter(FirewallRule.audit_id == audit_id).count()
        stored_objects = db_session.query(ObjectDefinition).filter(ObjectDefinition.audit_id == audit_id).count()
        
        assert stored_rules == 1500, f"Expected 1500 rules in database, found {stored_rules}"
        assert stored_objects == 750, f"Expected 750 objects in database, found {stored_objects}"
        
        logger.info(f"Successfully completed combined large dataset test in {total_duration:.3f} seconds")

    def test_bulk_insert_vs_individual_insert_comparison(self, db_session, sample_audit_session):
        """Compare bulk insert performance vs individual inserts (for reference)."""
        logger.info("Comparing bulk insert vs individual insert performance")
        
        # Create moderate dataset for comparison
        test_rules = create_large_rules_dataset(100)
        audit_id = sample_audit_session.id
        
        # Test bulk insert (current implementation)
        bulk_start_time = time.time()
        bulk_stored = store_rules(db_session, audit_id, test_rules)
        bulk_duration = time.time() - bulk_start_time
        
        logger.info(f"Bulk insert: {bulk_stored} rules in {bulk_duration:.3f}s ({bulk_stored/bulk_duration:.1f} rules/sec)")
        
        # Verify bulk insert worked
        assert bulk_stored == 100, f"Expected 100 rules from bulk insert, got {bulk_stored}"
        assert bulk_duration < 1.0, f"Bulk insert should be fast, took {bulk_duration:.3f}s"
        
        # Clean up for individual insert test
        from src.models import FirewallRule
        db_session.query(FirewallRule).filter(FirewallRule.audit_id == audit_id).delete()
        db_session.commit()

        # Test individual insert (for comparison - not recommended for production)
        individual_start_time = time.time()
        individual_stored = 0
        
        for rule_data in test_rules[:10]:  # Only test 10 for speed
            rule = FirewallRule(
                audit_id=audit_id,
                rule_name=rule_data['rule_name'],
                rule_type=rule_data['rule_type'],
                src_zone=rule_data['src_zone'],
                dst_zone=rule_data['dst_zone'],
                src=rule_data['src'],
                dst=rule_data['dst'],
                service=rule_data['service'],
                action=rule_data['action'],
                position=rule_data['position'],
                is_disabled=rule_data['is_disabled'],
                raw_xml=rule_data['raw_xml']
            )
            db_session.add(rule)
            individual_stored += 1
        
        db_session.commit()
        individual_duration = time.time() - individual_start_time
        
        logger.info(f"Individual insert: {individual_stored} rules in {individual_duration:.3f}s ({individual_stored/individual_duration:.1f} rules/sec)")
        
        # Calculate performance improvement
        bulk_rate = bulk_stored / bulk_duration
        individual_rate = individual_stored / individual_duration
        improvement_factor = bulk_rate / individual_rate
        
        logger.info(f"Bulk insert is {improvement_factor:.1f}x faster than individual inserts")
        
        # Bulk insert should be significantly faster
        assert improvement_factor > 2.0, f"Bulk insert should be at least 2x faster, got {improvement_factor:.1f}x"
        
        logger.info("Bulk insert performance comparison completed successfully")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
