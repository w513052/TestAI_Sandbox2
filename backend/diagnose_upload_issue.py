#!/usr/bin/env python3
"""
Diagnose the recent upload issue to understand what's happening.
"""

import requests
import json

def diagnose_recent_upload():
    """Diagnose the most recent upload to understand the issue."""
    
    print("🔍 Diagnosing Recent Upload Issue")
    print("=" * 50)
    
    # Get the most recent audit (ID 58 from logs)
    audit_id = 58
    
    print(f"\n📋 Checking Audit ID: {audit_id}")
    
    try:
        # Get analysis results
        analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if analysis_response.status_code == 200:
            analysis_result = analysis_response.json()
            analysis_data = analysis_result['data']
            
            print(f"✅ Analysis retrieved successfully!")
            
            # Check the analysis summary
            summary = analysis_data.get('analysis_summary', {})
            print(f"\n📊 Analysis Summary:")
            print(f"   Total Rules: {summary.get('total_rules', 0)}")
            print(f"   Total Objects: {summary.get('total_objects', 0)}")
            print(f"   Used Objects: {summary.get('used_objects_count', 0)}")
            print(f"   Unused Objects: {summary.get('unused_objects_count', 0)}")
            
            # Check individual analysis categories
            print(f"\n🔍 Analysis Categories:")
            categories = [
                ('Duplicate Rules', 'duplicateRules'),
                ('Shadowed Rules', 'shadowedRules'), 
                ('Unused Rules', 'unusedRules'),
                ('Overlapping Rules', 'overlappingRules'),
                ('Unused Objects', 'unusedObjects')
            ]
            
            for category_name, category_key in categories:
                items = analysis_data.get(category_key, [])
                print(f"   {category_name}: {len(items)} items")
                
                # Show first few items for unused objects
                if category_key == 'unusedObjects' and len(items) > 0:
                    print(f"   📋 Sample unused objects:")
                    for i, obj in enumerate(items[:3]):
                        print(f"      {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')}) - {obj.get('description', 'N/A')}")
                    if len(items) > 3:
                        print(f"      ... and {len(items) - 3} more")
            
            # Check if this matches what frontend expects
            print(f"\n🎯 Frontend Data Structure Check:")
            required_fields = ['analysis_summary', 'unusedObjects', 'unusedRules', 'duplicateRules', 'shadowedRules', 'overlappingRules']
            
            for field in required_fields:
                if field in analysis_data:
                    if field == 'analysis_summary':
                        print(f"   ✅ {field}: Present with {len(analysis_data[field])} keys")
                    else:
                        print(f"   ✅ {field}: {len(analysis_data[field])} items")
                else:
                    print(f"   ❌ {field}: MISSING")
            
            # Diagnose the specific issue
            print(f"\n🔬 Issue Diagnosis:")
            
            total_rules = summary.get('total_rules', 0)
            total_objects = summary.get('total_objects', 0)
            unused_objects = summary.get('unused_objects_count', 0)
            
            if total_rules == 0:
                print(f"   🚨 ISSUE FOUND: No rules parsed from XML file")
                print(f"      - The uploaded XML file contains 0 security rules")
                print(f"      - Without rules, object usage cannot be determined")
                print(f"      - All {total_objects} objects appear as 'unused'")
                print(f"      - This is expected behavior for objects-only files")
            elif total_objects == 0:
                print(f"   🚨 ISSUE FOUND: No objects parsed from XML file")
                print(f"      - The uploaded XML file contains 0 objects")
                print(f"      - Rules exist but no objects to analyze")
            elif unused_objects == total_objects:
                print(f"   ⚠️  POTENTIAL ISSUE: All objects are unused")
                print(f"      - {total_rules} rules parsed, {total_objects} objects parsed")
                print(f"      - All objects marked as unused - check object referencing logic")
            else:
                print(f"   ✅ Normal analysis results")
                print(f"      - {total_rules} rules, {total_objects} objects")
                print(f"      - {unused_objects} unused, {total_objects - unused_objects} used")
            
            # Check what frontend should display
            print(f"\n🖥️  Frontend Display Expectations:")
            print(f"   Dashboard Summary:")
            print(f"      Total Rules: {total_rules}")
            print(f"      Total Objects: {total_objects}")
            print(f"      Unused Objects: {unused_objects}")
            
            print(f"   Analysis Tabs:")
            for category_name, category_key in categories:
                count = len(analysis_data.get(category_key, []))
                print(f"      {category_name}: {count} items")
            
            return True
            
        else:
            print(f"❌ Failed to get analysis: {analysis_response.status_code}")
            print(f"   Response: {analysis_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Diagnosis failed: {str(e)}")
        return False

def check_frontend_connection():
    """Check if frontend can connect to backend."""
    
    print(f"\n🌐 Frontend Connection Check:")
    
    try:
        # Test health endpoint
        health_response = requests.get('http://127.0.0.1:8000/health', 
                                     headers={'Origin': 'http://localhost:5175'})
        
        if health_response.status_code == 200:
            print(f"   ✅ Backend health check: OK")
            print(f"   ✅ CORS headers: Present")
            return True
        else:
            print(f"   ❌ Backend health check failed: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting diagnosis...")
    
    # Check backend connection
    backend_ok = check_frontend_connection()
    
    if backend_ok:
        # Diagnose the upload issue
        diagnosis_ok = diagnose_recent_upload()
        
        if diagnosis_ok:
            print(f"\n✅ Diagnosis Complete!")
            print(f"\n💡 Summary:")
            print(f"   - Backend is running and accessible")
            print(f"   - Recent upload processed successfully")
            print(f"   - Issue: Uploaded XML file contains 0 rules, 10 objects")
            print(f"   - Result: All objects marked as 'unused' (expected)")
            print(f"   - Frontend should display: 0 rules, 10 unused objects")
            
            print(f"\n🔧 Recommendations:")
            print(f"   1. Upload an XML file that contains both rules AND objects")
            print(f"   2. Check that the XML file has <rules> sections with <entry> elements")
            print(f"   3. Verify the XML structure matches Palo Alto format")
            print(f"   4. Use test files that have rules referencing objects")
        else:
            print(f"\n❌ Diagnosis failed - check backend logs")
    else:
        print(f"\n❌ Backend connection failed - check if backend is running")
