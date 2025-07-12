#!/usr/bin/env python3
"""
Debug the analysis endpoint error to see what's causing the 500 error.
"""

def debug_analysis_error():
    """Debug the analysis endpoint error."""
    
    print("🔍 DEBUGGING ANALYSIS ENDPOINT ERROR")
    print("=" * 50)
    
    try:
        # Test the analysis function directly
        from src.utils.parse_config import analyze_rule_usage
        
        # Get a SET format audit ID
        import sqlite3
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM audit_sessions 
            WHERE filename LIKE '%sample4%'
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        audit = cursor.fetchone()
        if not audit:
            print("❌ No SET audit found")
            return
        
        audit_id = audit[0]
        print(f"📋 Testing analyze_rule_usage({audit_id})...")
        
        conn.close()
        
        # Call the function directly to see the error
        result = analyze_rule_usage(audit_id)
        
        print(f"✅ analyze_rule_usage worked!")
        print(f"   Results: {list(result.keys())}")
        
        # Now test the analysis endpoint logic
        print(f"\n🔧 Testing analysis endpoint logic...")
        
        from src.routers.audits import get_analysis
        from fastapi import HTTPException
        from sqlalchemy.orm import Session
        from src.database import get_db
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Call the analysis endpoint function directly
            analysis_result = get_analysis(audit_id, db)
            print(f"✅ Analysis endpoint worked!")
            print(f"   Keys: {list(analysis_result.keys())}")
        except Exception as e:
            print(f"❌ Analysis endpoint failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 DEBUGGING ANALYSIS ENDPOINT ERROR")
    print("=" * 60)
    
    success = debug_analysis_error()
    
    if success:
        print(f"\n✅ Debug completed")
    else:
        print(f"\n❌ Debug failed")
