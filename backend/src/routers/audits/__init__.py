from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import AuditSession, FirewallRule, ObjectDefinition
from src.utils.parse_config import (
    validate_xml_file,
    compute_file_hash,
    parse_rules,
    parse_objects,
    parse_metadata,
    parse_set_config,
    store_rules,
    store_objects,
    analyze_object_usage
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
                # Parse set format configuration
                logger.info(f"Processing set format file: {file.content_type}")
                try:
                    set_content = file_content.decode('utf-8')
                    logger.info(f"Decoded set content, length: {len(set_content)} characters")
                    rules_data, objects_data, config_metadata = parse_set_config(set_content)
                    logger.info(f"Set format parsing completed: {len(rules_data)} rules, {len(objects_data)} objects")
                except UnicodeDecodeError:
                    logger.error("Failed to decode set format file as UTF-8")
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "ENCODING_ERROR",
                            "message": "Set format file must be UTF-8 encoded"
                        }
                    )
                
        except ValueError as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "PARSING_ERROR",
                    "message": str(e)
                }
            )
        
        # Create audit session with enhanced validation and error handling
        try:
            # Validate session name length
            final_session_name = session_name or f"Audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            if len(final_session_name) > 255:
                final_session_name = final_session_name[:255]
                logger.warning(f"Session name truncated to 255 characters: {final_session_name}")

            # Validate filename
            if not file.filename or len(file.filename) > 255:
                logger.warning(f"Invalid filename: {file.filename}")
                safe_filename = (file.filename or "unknown_file")[:255]
            else:
                safe_filename = file.filename

            # Create audit session record
            audit_session = AuditSession(
                session_name=final_session_name,
                filename=safe_filename,
                file_hash=file_hash,
                start_time=datetime.utcnow(),
                config_metadata=config_metadata or {}
            )

            # Store audit session in database with transaction management
            db.add(audit_session)
            db.commit()
            db.refresh(audit_session)

            audit_id = audit_session.id
            logger.info(f"Audit session created successfully with ID: {audit_id}, Name: '{final_session_name}', File: '{safe_filename}'")

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create audit session: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "DATABASE_ERROR",
                    "message": "Failed to create audit session in database"
                }
            )
        
        # Analyze object usage in rules before storage
        try:
            if rules_data and objects_data:
                object_usage = analyze_object_usage(rules_data, objects_data)
                logger.info(f"Object usage analysis completed for {len(object_usage)} objects")
        except Exception as e:
            logger.warning(f"Object usage analysis failed: {str(e)}")
            # Continue without usage analysis

        # Store parsed rules using batch operations
        try:
            rules_stored = store_rules(db, audit_id, rules_data)
            logger.info(f"Batch storage completed: {rules_stored} rules stored")
        except Exception as e:
            logger.error(f"Error during batch rules storage: {str(e)}")
            # Don't fail the entire operation if rules storage fails
            rules_stored = 0

        # Store parsed objects using batch operations
        try:
            objects_stored = store_objects(db, audit_id, objects_data)
            logger.info(f"Batch storage completed: {objects_stored} objects stored")
        except Exception as e:
            logger.error(f"Error during batch objects storage: {str(e)}")
            # Don't fail the entire operation if objects storage fails
            objects_stored = 0

        # Final commit for all data
        try:
            db.commit()
            logger.info(f"Database transaction committed successfully for audit session {audit_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to commit database transaction: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "DATABASE_COMMIT_ERROR",
                    "message": "Failed to save parsed data to database"
                }
            )

        # Update audit session with end time to mark completion
        try:
            audit_session.end_time = datetime.utcnow()
            db.commit()
            logger.info(f"Audit session {audit_id} marked as completed")
        except Exception as e:
            logger.warning(f"Failed to update end_time for audit session {audit_id}: {str(e)}")
            # Don't fail the operation if end_time update fails
        
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
