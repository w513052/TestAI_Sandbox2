#!/usr/bin/env python3
"""
Debug what the frontend is actually receiving vs what the backend is sending.
"""

import requests
import json

def debug_frontend_output():
    """Debug the frontend output issue."""
    
    print("🔍 DEBUGGING FRONTEND OUTPUT ISSUE")
    print("=" * 50)
    
    try:
        # Get the most recent audit (should be our successful test)
        response = requests.get('http://127.0.0.1:8000/api/v1/audits')
        if response.status_code == 200:
            audits = response.json()['data']
            if audits:
                latest_audit = audits[0]
                audit_id = latest_audit['audit_id']
                filename = latest_audit['filename']
                
                print(f"📋 Most Recent Audit:")
                print(f"   ID: {audit_id}")
                print(f"   File: {filename}")
                
                # Get the analysis data that frontend receives
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    
                    print(f"\n📊 Raw API Response Structure:")
                    print(f"   Response keys: {list(analysis_result.keys())}")
                    
                    if 'data' in analysis_result:
                        analysis_data = analysis_result['data']
                        print(f"   Data keys: {list(analysis_data.keys())}")
                        
                        # Check analysis summary
                        if 'analysis_summary' in analysis_data:
                            summary = analysis_data['analysis_summary']
                            print(f"\n📈 Analysis Summary (Backend):")
                            for key, value in summary.items():
                                print(f"      {key}: {value}")
                        
                        # Check each analysis category
                        categories = {
                            'unusedObjects': 'Unused Objects',
                            'redundantObjects': 'Redundant Objects', 
                            'unusedRules': 'Unused Rules',
                            'duplicateRules': 'Duplicate Rules',
                            'shadowedRules': 'Shadowed Rules',
                            'overlappingRules': 'Overlapping Rules'
                        }
                        
                        print(f"\n📋 Analysis Categories (Backend):")
                        for key, name in categories.items():
                            if key in analysis_data:
                                items = analysis_data[key]
                                print(f"   {name}: {len(items)} items")
                                
                                # Show sample items for verification
                                if len(items) > 0 and key in ['unusedObjects', 'redundantObjects']:
                                    print(f"      Sample items:")
                                    for i, item in enumerate(items[:3]):
                                        print(f"      {i+1}. {item.get('name', 'N/A')} = {item.get('value', 'N/A')}")
                            else:
                                print(f"   {name}: MISSING ❌")
                        
                        # Simulate what FileUpload.tsx does
                        print(f"\n🖥️  Frontend Data Processing Simulation:")
                        
                        # Get metadata from upload response (simulate)
                        upload_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}')
                        if upload_response.status_code == 200:
                            upload_data = upload_response.json()['data']
                            metadata = upload_data.get('metadata', {})
                            
                            print(f"   Upload metadata: {metadata}")
                            
                            # Calculate total objects like frontend does
                            total_objects = metadata.get('address_object_count', 0) + metadata.get('service_object_count', 0)
                            
                            # Create frontend data structure
                            frontend_data = {
                                "summary": {
                                    "totalRules": metadata.get('rules_parsed', 0),
                                    "totalObjects": total_objects,
                                    "duplicateRules": len(analysis_data.get('duplicateRules', [])),
                                    "shadowedRules": len(analysis_data.get('shadowedRules', [])),
                                    "unusedRules": len(analysis_data.get('unusedRules', [])),
                                    "overlappingRules": len(analysis_data.get('overlappingRules', [])),
                                    "unusedObjects": len(analysis_data.get('unusedObjects', [])),
                                    "redundantObjects": len(analysis_data.get('redundantObjects', 0)),
                                    "analysisDate": upload_data.get('start_time', ''),
                                    "configVersion": metadata.get('firmware_version', 'Unknown'),
                                    "auditId": audit_id,
                                    "fileName": filename,
                                    "fileHash": upload_data.get('file_hash', ''),
                                }
                            }
                            
                            print(f"\n📊 Frontend Summary Data:")
                            for key, value in frontend_data["summary"].items():
                                if key not in ['analysisDate', 'fileHash', 'fileName', 'auditId', 'configVersion']:
                                    print(f"      {key}: {value}")
                            
                            # Compare backend vs frontend calculations
                            print(f"\n🔍 Backend vs Frontend Comparison:")
                            
                            backend_summary = analysis_data.get('analysis_summary', {})
                            
                            comparisons = [
                                ('totalRules', 'total_rules'),
                                ('totalObjects', 'total_objects'),
                                ('unusedObjects', 'unused_objects_count'),
                                ('redundantObjects', 'redundant_objects_count')
                            ]
                            
                            discrepancies = []
                            for frontend_key, backend_key in comparisons:
                                frontend_val = frontend_data["summary"][frontend_key]
                                backend_val = backend_summary.get(backend_key, 0)
                                
                                status = "✅" if frontend_val == backend_val else "❌"
                                print(f"      {frontend_key}: Frontend={frontend_val}, Backend={backend_val} {status}")
                                
                                if frontend_val != backend_val:
                                    discrepancies.append((frontend_key, frontend_val, backend_val))
                            
                            if discrepancies:
                                print(f"\n🚨 DISCREPANCIES FOUND:")
                                for key, frontend_val, backend_val in discrepancies:
                                    print(f"   {key}: Frontend shows {frontend_val}, Backend has {backend_val}")
                                    
                                    if key == 'totalObjects':
                                        print(f"      Frontend calculation: address_objects({metadata.get('address_object_count', 0)}) + service_objects({metadata.get('service_object_count', 0)}) = {total_objects}")
                                        print(f"      Backend calculation: {backend_val}")
                                        
                                        if total_objects != backend_val:
                                            print(f"      ❌ Object count calculation mismatch!")
                                            print(f"      This could cause frontend to show wrong totals")
                                
                                return False
                            else:
                                print(f"\n✅ No discrepancies found between backend and frontend calculations")
                                return True
                        else:
                            print(f"❌ Could not get upload metadata")
                            return False
                    else:
                        print(f"❌ No 'data' key in analysis response")
                        return False
                else:
                    print(f"❌ Analysis request failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ No audits found")
                return False
        else:
            print(f"❌ Failed to get audits: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return False

def check_frontend_console_logs():
    """Provide instructions for checking frontend console logs."""
    
    print(f"\n🖥️  Frontend Console Debug Instructions")
    print("=" * 50)
    
    print(f"📋 To debug frontend display issues:")
    print(f"   1. Open browser Developer Tools (F12)")
    print(f"   2. Go to Console tab")
    print(f"   3. Upload a file and look for these debug logs:")
    print(f"      - '🎯 Frontend Analysis Data:'")
    print(f"      - '📊 Summary:'") 
    print(f"      - '📦 Unused Objects:'")
    print(f"      - '🚀 App received analysis data:'")
    print(f"      - '🖥️ Dashboard received data:'")
    
    print(f"\n🔍 Common Issues to Check:")
    print(f"   - JavaScript errors in console (red text)")
    print(f"   - Network errors in Network tab")
    print(f"   - API calls returning wrong data")
    print(f"   - Frontend state not updating")
    print(f"   - Component rendering issues")
    
    print(f"\n💡 If frontend shows wrong numbers:")
    print(f"   - Check if API response matches backend calculations")
    print(f"   - Verify frontend data processing logic")
    print(f"   - Ensure components are receiving correct props")
    print(f"   - Check for caching issues (hard refresh: Ctrl+F5)")

if __name__ == "__main__":
    print("🚀 DEBUGGING FRONTEND OUTPUT ISSUE")
    print("=" * 60)
    
    success = debug_frontend_output()
    
    if success:
        print(f"\n✅ BACKEND DATA IS CORRECT")
        print(f"   The issue is likely in frontend JavaScript code")
        check_frontend_console_logs()
    else:
        print(f"\n❌ BACKEND DATA HAS ISSUES")
        print(f"   Need to fix backend calculations first")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Check browser console for JavaScript errors")
    print(f"   2. Verify API responses match backend calculations") 
    print(f"   3. Test with a fresh file upload")
    print(f"   4. Check if frontend components are updating correctly")
