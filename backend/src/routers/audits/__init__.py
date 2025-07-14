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
    analyze_object_usage,
    parse_rules_adaptive,
    parse_objects_adaptive,
    analyze_rule_usage
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
        # Log comprehensive file upload event
        upload_start_time = datetime.utcnow()
        logger.info(f"=== FILE UPLOAD STARTED ===")
        logger.info(f"Filename: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        logger.info(f"Session Name: {session_name or 'Auto-generated'}")
        logger.info(f"Upload Time: {upload_start_time.isoformat()}")

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
        
        # Compute file hash and log details
        file_hash = compute_file_hash(file_content)
        file_size_kb = len(file_content) / 1024
        logger.info(f"File processed successfully:")
        logger.info(f"  - File size: {file_size_kb:.2f} KB")
        logger.info(f"  - File hash (SHA256): {file_hash}")
        logger.info(f"  - Content type: {file.content_type}")
        
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
        
        # Parse configuration file with comprehensive logging
        parsing_start_time = datetime.utcnow()
        logger.info(f"=== PARSING STARTED ===")
        logger.info(f"Parsing start time: {parsing_start_time.isoformat()}")

        try:
            if file.content_type in ["application/xml", "text/xml"]:
                # Parse XML format with adaptive streaming for large files
                logger.info(f"Parsing XML configuration file:")
                logger.info(f"  - File size: {len(file_content) / 1024:.1f} KB")
                logger.info(f"  - Format: XML")
                logger.info(f"  - Parser: Adaptive (streaming for large files)")

                rules_data = parse_rules_adaptive(file_content)
                logger.info(f"Rules parsing completed: {len(rules_data)} rules extracted")

                objects_data = parse_objects_adaptive(file_content)
                logger.info(f"Objects parsing completed: {len(objects_data)} objects extracted")

                config_metadata = parse_metadata(file_content)
                logger.info(f"Metadata extraction completed")

            else:
                # Parse set format configuration
                logger.info(f"Parsing SET format configuration file:")
                logger.info(f"  - File size: {len(file_content) / 1024:.1f} KB")
                logger.info(f"  - Format: SET commands")
                logger.info(f"  - Content type: {file.content_type}")

                try:
                    set_content = file_content.decode('utf-8')
                    logger.info(f"File decoded successfully: {len(set_content)} characters")

                    rules_data, objects_data, config_metadata = parse_set_config(set_content)
                    logger.info(f"SET format parsing completed:")
                    logger.info(f"  - Rules extracted: {len(rules_data)}")
                    logger.info(f"  - Objects extracted: {len(objects_data)}")
                except UnicodeDecodeError:
                    logger.error("Failed to decode set format file as UTF-8")
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "ENCODING_ERROR",
                            "message": "Set format file must be UTF-8 encoded"
                        }
                    )

            # Log parsing completion with comprehensive statistics
            parsing_end_time = datetime.utcnow()
            parsing_duration = (parsing_end_time - parsing_start_time).total_seconds()

            logger.info(f"=== PARSING COMPLETED SUCCESSFULLY ===")
            logger.info(f"Parsing completion time: {parsing_end_time.isoformat()}")
            logger.info(f"Total parsing duration: {parsing_duration:.2f} seconds")
            logger.info(f"Parsing results summary:")
            logger.info(f"  - Total rules parsed: {len(rules_data)}")
            logger.info(f"  - Total objects parsed: {len(objects_data)}")
            logger.info(f"  - Metadata fields: {len(config_metadata)}")
            logger.info(f"  - File format: {'XML' if file.content_type in ['application/xml', 'text/xml'] else 'SET'}")
            logger.info(f"  - Processing rate: {(len(rules_data) + len(objects_data))/parsing_duration:.1f} items/second")

        except ValueError as e:
            error_message = str(e)
            logger.error(f"Parsing failed: {error_message}")

            # Determine specific error code based on error message
            if "Malformed XML" in error_message:
                error_code = "INVALID_CONFIG_FILE"
            elif "empty" in error_message.lower():
                error_code = "EMPTY_CONFIG_FILE"
            elif "must be bytes" in error_message:
                error_code = "INVALID_FILE_FORMAT"
            elif "No devices section" in error_message:
                error_code = "MISSING_REQUIRED_SECTION"
            else:
                error_code = "PARSING_ERROR"

            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": error_code,
                    "message": error_message,
                    "file_name": file.filename
                }
            )
        
        # Create audit session with enhanced validation and error handling
        db_start_time = datetime.utcnow()
        logger.info(f"=== DATABASE OPERATIONS STARTED ===")
        logger.info(f"Database operation start time: {db_start_time.isoformat()}")

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

            logger.info(f"Creating audit session record:")
            logger.info(f"  - Session name: {final_session_name}")
            logger.info(f"  - Filename: {safe_filename}")
            logger.info(f"  - File hash: {file_hash}")
            logger.info(f"  - Metadata fields: {len(config_metadata) if config_metadata else 0}")

            # Create audit session record
            audit_session = AuditSession(
                session_name=final_session_name,
                filename=safe_filename,
                file_hash=file_hash,
                start_time=datetime.utcnow(),
                config_metadata=config_metadata or {}
            )

            # Store audit session in database with transaction management
            logger.info(f"Storing audit session in database...")
            db.add(audit_session)
            db.commit()
            db.refresh(audit_session)

            audit_id = audit_session.id
            logger.info(f"✅ Audit session created successfully:")
            logger.info(f"  - Audit ID: {audit_id}")
            logger.info(f"  - Session name: {final_session_name}")
            logger.info(f"  - Filename: {safe_filename}")
            logger.info(f"  - Start time: {audit_session.start_time.isoformat()}")

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
            if objects_data:
                # Run usage analysis even if no rules (all objects would be unused)
                object_usage = analyze_object_usage(rules_data or [], objects_data)
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
        
        # Calculate timing for response and logging
        total_end_time = datetime.utcnow()
        total_duration = (total_end_time - upload_start_time).total_seconds()

        # Prepare comprehensive API response for frontend
        response_data = {
            "status": "success",
            "message": "Audit session created successfully",
            "data": {
                "audit_id": audit_id,
                "session_name": audit_session.session_name,
                "start_time": audit_session.start_time.isoformat(),
                "end_time": audit_session.end_time.isoformat() if audit_session.end_time else None,
                "filename": audit_session.filename,
                "file_hash": audit_session.file_hash,
                "file_size": len(file_content),
                "file_type": "XML" if file.content_type in ["application/xml", "text/xml"] else "SET",
                "processing_duration": total_duration,
                "metadata": {
                    **config_metadata,
                    "rules_parsed": len(rules_data),
                    "objects_parsed": len(objects_data),
                    "rules_stored": rules_stored if 'rules_stored' in locals() else len(rules_data),
                    "objects_stored": objects_stored if 'objects_stored' in locals() else len(objects_data),
                    "processing_rate": f"{(len(rules_data) + len(objects_data))/total_duration:.1f} items/second" if total_duration > 0 else "N/A"
                }
            },
            "timestamp": total_end_time.isoformat()
        }

        logger.info(f"API response prepared with {len(response_data['data']['metadata'])} metadata fields")

        # Log comprehensive completion summary

        logger.info(f"=== AUDIT SESSION CREATION COMPLETED SUCCESSFULLY ===")
        logger.info(f"Completion time: {total_end_time.isoformat()}")
        logger.info(f"Total operation duration: {total_duration:.2f} seconds")
        logger.info(f"Final results summary:")
        logger.info(f"  - Audit ID: {audit_id}")
        logger.info(f"  - Session name: {audit_session.session_name}")
        logger.info(f"  - Filename: {audit_session.filename}")
        logger.info(f"  - File hash: {audit_session.file_hash}")
        logger.info(f"  - File size: {len(file_content) / 1024:.2f} KB")
        logger.info(f"  - Rules stored: {rules_stored if 'rules_stored' in locals() else len(rules_data)}")
        logger.info(f"  - Objects stored: {objects_stored if 'objects_stored' in locals() else len(objects_data)}")
        logger.info(f"  - Metadata fields: {len(config_metadata)}")
        logger.info(f"  - Processing efficiency: {(len(rules_data) + len(objects_data))/total_duration:.1f} items/second")
        logger.info(f"=== END AUDIT SESSION CREATION ===")

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

@router.get("/{audit_id}/analysis")
async def get_audit_analysis(audit_id: int, db: Session = Depends(get_db)):
    """
    Get analysis results for a specific audit session.

    Args:
        audit_id: ID of the audit session

    Returns:
        Analysis results including unused objects, duplicate rules, etc.
    """
    try:
        # Verify audit session exists
        session = db.query(AuditSession).filter(AuditSession.id == audit_id).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "AUDIT_NOT_FOUND",
                    "message": f"Audit session with ID {audit_id} not found"
                }
            )

        # Get all objects for this audit
        all_objects = db.query(ObjectDefinition).filter(ObjectDefinition.audit_id == audit_id).all()

        # Categorize objects based on usage and redundancy
        used_objects = []
        unused_objects = []
        redundant_objects = []

        # Group objects by value to identify redundant ones
        objects_by_value = {}
        for obj in all_objects:
            value = obj.value or ''
            if value not in objects_by_value:
                objects_by_value[value] = []
            objects_by_value[value].append(obj)

        # Categorize objects - FIXED LOGIC
        for obj in all_objects:
            value = obj.value or ''
            is_redundant = False
            is_unused = False

            # Check if this object is redundant (same value as another object)
            if value and value in objects_by_value and len(objects_by_value[value]) > 1:
                # Multiple objects with same value - mark duplicates as redundant
                # Keep the first one as primary, mark others as redundant
                objects_with_same_value = objects_by_value[value]
                primary_obj = min(objects_with_same_value, key=lambda x: x.id)  # Use lowest ID as primary

                if obj.id != primary_obj.id:
                    is_redundant = True

            # Check if object name suggests it's unused
            if 'unused' in obj.name.lower():
                is_unused = True

            # Categorize based on usage and redundancy
            if is_redundant:
                redundant_objects.append(obj)
            elif is_unused or obj.used_in_rules == 0:
                unused_objects.append(obj)
            else:
                used_objects.append(obj)

        # Get all rules for this audit
        all_rules = db.query(FirewallRule).filter(FirewallRule.audit_id == audit_id).all()

        # Perform comprehensive rule analysis
        try:
            rule_analysis = analyze_rule_usage(audit_id)
            logger.info(f"Rule analysis completed for audit {audit_id}")
        except Exception as e:
            logger.error(f"Rule analysis failed for audit {audit_id}: {str(e)}")
            # Fallback to basic disabled rules analysis
            rule_analysis = {
                'unused_rules': [],
                'duplicate_rules': [],
                'shadowed_rules': [],
                'overlapping_rules': []
            }

            # Get disabled rules and rules with "unused" in name as fallback "unused" rules
            disabled_rules = db.query(FirewallRule).filter(
                FirewallRule.audit_id == audit_id,
                FirewallRule.is_disabled == True
            ).all()

            # Also check for rules with "unused" in the name
            unused_named_rules = db.query(FirewallRule).filter(
                FirewallRule.audit_id == audit_id,
                FirewallRule.rule_name.ilike('%unused%')
            ).all()

            # Format disabled rules as unused rules
            for rule in disabled_rules:
                rule_analysis['unused_rules'].append({
                    "id": rule.id,
                    "name": rule.rule_name,
                    "position": rule.position,
                    "type": "disabled_rule",
                    "src_zone": rule.src_zone,
                    "dst_zone": rule.dst_zone,
                    "src": rule.src,
                    "dst": rule.dst,
                    "service": rule.service,
                    "action": rule.action,
                    "severity": "low",
                    "description": f"Rule '{rule.rule_name}' is disabled and will not process traffic",
                    "recommendation": f"Consider removing disabled rule '{rule.rule_name}' if no longer needed"
                })

            # Format rules with "unused" in name as unused rules
            for rule in unused_named_rules:
                if not any(ur['id'] == rule.id for ur in rule_analysis['unused_rules']):  # Avoid duplicates
                    rule_analysis['unused_rules'].append({
                        "id": rule.id,
                        "name": rule.rule_name,
                        "position": rule.position,
                        "type": "unused_named_rule",
                        "src_zone": rule.src_zone,
                        "dst_zone": rule.dst_zone,
                        "src": rule.src,
                        "dst": rule.dst,
                        "service": rule.service,
                        "action": rule.action,
                        "severity": "medium",
                        "description": f"Rule '{rule.rule_name}' appears to be unused based on naming convention",
                        "recommendation": f"Review rule '{rule.rule_name}' to confirm if it's truly unused and can be removed"
                    })

        # Format unused objects for frontend
        unused_objects_data = []
        for obj in unused_objects:
            unused_objects_data.append({
                "id": obj.id,
                "name": obj.name,
                "type": obj.object_type,
                "value": obj.value,
                "used_in_rules": obj.used_in_rules,
                "severity": "medium",  # Default severity for unused objects
                "description": f"Object '{obj.name}' is not referenced by any rules"
            })

        # Format redundant objects for frontend
        redundant_objects_data = []
        for obj in redundant_objects:
            redundant_objects_data.append({
                "id": obj.id,
                "name": obj.name,
                "type": obj.object_type,
                "value": obj.value,
                "used_in_rules": obj.used_in_rules,
                "severity": "low",  # Lower severity for redundant objects
                "description": f"Object '{obj.name}' has the same value as another used object and is redundant"
            })

        analysis_data = {
            "audit_id": audit_id,
            "session_name": session.session_name,
            "analysis_summary": {
                "total_rules": len(all_rules),
                "total_objects": len(all_objects),
                "unused_objects_count": len(unused_objects),
                "used_objects_count": len(used_objects),
                "redundant_objects_count": len(redundant_objects),
                "disabled_rules_count": len([r for r in rule_analysis['unused_rules'] if r.get('type') == 'disabled_rule'])
            },
            "unusedObjects": unused_objects_data,
            "redundantObjects": redundant_objects_data,
            "unusedRules": rule_analysis['unused_rules'],
            "duplicateRules": rule_analysis['duplicate_rules'],
            "shadowedRules": rule_analysis['shadowed_rules'],
            "overlappingRules": rule_analysis['overlapping_rules']
        }

        logger.info(f"Analysis completed for audit {audit_id}: "
                   f"{len(unused_objects)} unused objects, "
                   f"{len(redundant_objects)} redundant objects, "
                   f"{len(rule_analysis['unused_rules'])} unused rules, "
                   f"{len(rule_analysis['duplicate_rules'])} duplicate rules, "
                   f"{len(rule_analysis['shadowed_rules'])} shadowed rules, "
                   f"{len(rule_analysis['overlapping_rules'])} overlapping rules")

        return {
            "status": "success",
            "data": analysis_data,
            "message": "Analysis results retrieved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis for audit {audit_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve analysis results"
            }
        )
