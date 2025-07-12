from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import AuditSession, FirewallRule, ObjectDefinition
from src.utils.parse_config import (
    validate_xml_file, 
    compute_file_hash, 
    parse_rules, 
    parse_objects, 
    parse_metadata
)
from src.utils.logging import logger
from datetime import datetime
from typing import Optional
import json

router = APIRouter(prefix="/api/v1/audits", tags=["audits"])

@router.post("/")
async def create_audit_session(
    file: UploadFile = File(...),
    session_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new audit session by uploading a Palo Alto configuration file.
    
    Args:
        file: Uploaded configuration file (XML or set format)
        session_name: Optional name for the audit session
        db: Database session
        
    Returns:
        JSON response with audit session details
    """
    try:
        # Log file upload event
        logger.info(f"File upload started: {file.filename}, session_name: {session_name}")
        
        # Validate file content type
        if file.content_type not in ["application/xml", "text/xml", "text/plain"]:
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INVALID_FILE_TYPE",
                    "message": f"Invalid file type. Expected XML or text file, got {file.content_type}"
                }
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            logger.error("Empty file uploaded")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "EMPTY_FILE",
                    "message": "Uploaded file is empty"
                }
            )
        
        # Compute file hash
        file_hash = compute_file_hash(file_content)
        logger.info(f"File hash computed: {file_hash}")
        
        # Validate XML structure (if XML file)
        if file.content_type in ["application/xml", "text/xml"]:
            try:
                validate_xml_file(file_content)
            except ValueError as e:
                logger.error(f"XML validation failed: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_CONFIG_FILE",
                        "message": str(e)
                    }
                )
        
        # Parse configuration file
        try:
            if file.content_type in ["application/xml", "text/xml"]:
                # Parse XML format
                rules_data = parse_rules(file_content)
                objects_data = parse_objects(file_content)
                config_metadata = parse_metadata(file_content)
            else:
                # TODO: Implement set format parsing in next task
                rules_data = []
                objects_data = []
                config_metadata = {}
                
        except ValueError as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "PARSING_ERROR",
                    "message": str(e)
                }
            )
        
        # Create audit session
        audit_session = AuditSession(
            session_name=session_name or f"Audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            filename=file.filename,
            file_hash=file_hash,
            start_time=datetime.utcnow(),
            config_metadata=config_metadata
        )
        
        db.add(audit_session)
        db.commit()
        db.refresh(audit_session)
        
        audit_id = audit_session.id
        logger.info(f"Audit session created with ID: {audit_id}")
        
        # Store parsed rules
        if rules_data:
            for rule_data in rules_data:
                rule = FirewallRule(
                    audit_id=audit_id,
                    **rule_data
                )
                db.add(rule)
            
            logger.info(f"Stored {len(rules_data)} rules")
        
        # Store parsed objects
        if objects_data:
            for object_data in objects_data:
                obj = ObjectDefinition(
                    audit_id=audit_id,
                    **object_data
                )
                db.add(obj)
            
            logger.info(f"Stored {len(objects_data)} objects")
        
        db.commit()
        
        # Prepare response
        response_data = {
            "status": "success",
            "data": {
                "audit_id": audit_id,
                "session_name": audit_session.session_name,
                "start_time": audit_session.start_time.isoformat(),
                "filename": audit_session.filename,
                "file_hash": audit_session.file_hash,
                "metadata": {
                    **config_metadata,
                    "rules_parsed": len(rules_data),
                    "objects_parsed": len(objects_data)
                }
            },
            "message": "Audit session created successfully"
        }
        
        logger.info(f"Audit session creation completed successfully: {audit_id}")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during audit creation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during audit creation"
            }
        )

@router.get("/")
async def list_audit_sessions(db: Session = Depends(get_db)):
    """
    List all audit sessions.
    
    Returns:
        List of audit sessions with basic information
    """
    try:
        sessions = db.query(AuditSession).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "audit_id": session.id,
                "session_name": session.session_name,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "filename": session.filename,
                "metadata": session.config_metadata
            })
        
        return {
            "status": "success",
            "data": sessions_data,
            "message": f"Retrieved {len(sessions_data)} audit sessions"
        }
        
    except Exception as e:
        logger.error(f"Error listing audit sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve audit sessions"
            }
        )

@router.get("/{audit_id}")
async def get_audit_session(audit_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific audit session.
    
    Args:
        audit_id: ID of the audit session
        
    Returns:
        Detailed audit session information
    """
    try:
        session = db.query(AuditSession).filter(AuditSession.id == audit_id).first()
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "AUDIT_NOT_FOUND",
                    "message": f"Audit session with ID {audit_id} not found"
                }
            )
        
        # Count related records
        rules_count = db.query(FirewallRule).filter(FirewallRule.audit_id == audit_id).count()
        objects_count = db.query(ObjectDefinition).filter(ObjectDefinition.audit_id == audit_id).count()
        
        session_data = {
            "audit_id": session.id,
            "session_name": session.session_name,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "filename": session.filename,
            "file_hash": session.file_hash,
            "metadata": session.config_metadata,
            "rules_count": rules_count,
            "objects_count": objects_count
        }
        
        return {
            "status": "success",
            "data": session_data,
            "message": "Audit session retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit session {audit_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve audit session"
            }
        )
