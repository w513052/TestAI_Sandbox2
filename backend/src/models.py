from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime

class AuditSession(Base):
    __tablename__ = "audit_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(255), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    filename = Column(String(255))
    file_hash = Column(String(64))
    config_metadata = Column(JSON, default={})
    rules = relationship("FirewallRule", back_populates="audit")
    objects = relationship("ObjectDefinition", back_populates="audit")
    recommendations = relationship("Recommendation", back_populates="audit")
    reports = relationship("ReportFile", back_populates="audit")

class FirewallRule(Base):
    __tablename__ = "firewall_rules"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_sessions.id"), index=True)
    rule_name = Column(String(255))
    rule_type = Column(String(50))
    src_zone = Column(String(255))
    dst_zone = Column(String(255))
    src = Column(Text)
    dst = Column(Text)
    service = Column(Text)
    action = Column(String(50))
    position = Column(Integer)
    is_disabled = Column(Boolean, default=False)
    raw_xml = Column(Text, nullable=True)
    audit = relationship("AuditSession", back_populates="rules")
    issues = relationship("RuleIssue", back_populates="rule")

class RuleIssue(Base):
    __tablename__ = "rule_issues"
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("firewall_rules.id"), index=True)
    issue_type = Column(String(100))
    severity = Column(String(50))
    description = Column(Text)
    rule = relationship("FirewallRule", back_populates="issues")

class ObjectDefinition(Base):
    __tablename__ = "object_definitions"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_sessions.id"), index=True)
    object_type = Column(String(50))
    name = Column(String(255))
    value = Column(Text)
    used_in_rules = Column(Integer, default=0)
    raw_xml = Column(Text, nullable=True)
    audit = relationship("AuditSession", back_populates="objects")
    issues = relationship("ObjectIssue", back_populates="object")

class ObjectIssue(Base):
    __tablename__ = "object_issues"
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("object_definitions.id"), index=True)
    issue_type = Column(String(100))
    severity = Column(String(50))
    description = Column(Text)
    object = relationship("ObjectDefinition", back_populates="issues")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_sessions.id"), index=True)
    category = Column(String(100))
    priority = Column(String(50))
    title = Column(String(255))
    description = Column(Text)
    impact = Column(Text)
    audit = relationship("AuditSession", back_populates="recommendations")

class ReportFile(Base):
    __tablename__ = "report_files"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_sessions.id"), index=True)
    format = Column(String(50))
    filepath = Column(String(255))
    generated_at = Column(DateTime, default=datetime.utcnow)
    audit = relationship("AuditSession", back_populates="reports")
