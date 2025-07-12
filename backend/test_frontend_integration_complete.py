#!/usr/bin/env python3
"""
Test the complete frontend integration to verify what the frontend actually receives.
"""

import requests
import json
import time

def test_frontend_integration():
    """Test the complete frontend integration flow."""
    
    print("🧪 Testing Complete Frontend Integration")
    print("=" * 50)
    
    # Use our test file that we know works
    filename = "debug_test_config.xml"
    
    print(f"📤 Step 1: Upload file (simulating frontend upload)")
    
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "application/xml")}
            data = {"session_name": "Frontend Integration Test"}
            
            # Add CORS headers like frontend would
            headers = {'Origin': 'http://localhost:5175'}
            
            upload_response = requests.post(
                'http://127.0.0.1:8000/api/v1/audits/',
                files=files,
                data=data,
                headers=headers
            )
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                audit_id = result['data']['audit_id']
                metadata = result['data']['metadata']
                
                print(f"✅ Upload successful! Audit ID: {audit_id}")
                print(f"📊 Upload Response Metadata:")
                print(f"   Rules parsed: {metadata.get('rules_parsed', 0)}")
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                print(f"   Address objects: {metadata.get('address_object_count', 0)}")
                print(f"   Service objects: {metadata.get('service_object_count', 0)}")
                
                # Step 2: Get analysis results (what frontend does next)
                print(f"\n🔍 Step 2: Get analysis results (simulating frontend analysis call)")
                
                analysis_response = requests.get(
                    f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis',
                    headers=headers
                )
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    
                    print(f"✅ Analysis successful!")
                    print(f"📋 Raw API Response Structure:")
                    print(f"   Response keys: {list(analysis_result.keys())}")
                    
                    if 'data' in analysis_result:
                        analysis_data = analysis_result['data']
                        print(f"   Data keys: {list(analysis_data.keys())}")
                        
                        # Check analysis summary
                        if 'analysis_summary' in analysis_data:
                            summary = analysis_data['analysis_summary']
                            print(f"\n📈 Analysis Summary (what frontend receives):")
                            for key, value in summary.items():
                                print(f"   {key}: {value}")
                        
                        # Check analysis categories
                        print(f"\n📋 Analysis Categories (what frontend receives):")
                        categories = ['duplicateRules', 'shadowedRules', 'unusedRules', 'overlappingRules', 'unusedObjects']
                        
                        for category in categories:
                            if category in analysis_data:
                                items = analysis_data[category]
                                print(f"   {category}: {len(items)} items")
                                
                                # Show sample items
                                if len(items) > 0 and category == 'unusedObjects':
                                    print(f"      Sample unused objects:")
                                    for i, obj in enumerate(items[:3]):
                                        print(f"      {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')}) - {obj.get('description', 'N/A')}")
                            else:
                                print(f"   {category}: MISSING ❌")
                        
                        # Step 3: Simulate what frontend should do with this data
                        print(f"\n🖥️  Step 3: Frontend Data Processing Simulation")
                        
                        # Convert to frontend format (like FileUpload.tsx does)
                        total_objects = metadata.get('address_object_count', 0) + metadata.get('service_object_count', 0)
                        
                        frontend_data = {
                            "summary": {
                                "totalRules": metadata.get('rules_parsed', 0),
                                "totalObjects": total_objects,
                                "duplicateRules": len(analysis_data.get('duplicateRules', [])),
                                "shadowedRules": len(analysis_data.get('shadowedRules', [])),
                                "unusedRules": len(analysis_data.get('unusedRules', [])),
                                "overlappingRules": len(analysis_data.get('overlappingRules', [])),
                                "unusedObjects": len(analysis_data.get('unusedObjects', [])),
                                "redundantObjects": 0,
                                "analysisDate": result['data']['start_time'],
                                "configVersion": metadata.get('firmware_version', 'Unknown'),
                                "auditId": audit_id,
                                "fileName": filename,
                                "fileHash": result['data']['file_hash'],
                            },
                            "duplicateRules": analysis_data.get('duplicateRules', []),
                            "shadowedRules": analysis_data.get('shadowedRules', []),
                            "unusedRules": analysis_data.get('unusedRules', []),
                            "overlappingRules": analysis_data.get('overlappingRules', []),
                            "unusedObjects": analysis_data.get('unusedObjects', []),
                            "recommendations": []
                        }
                        
                        print(f"📊 Frontend Summary Data:")
                        for key, value in frontend_data["summary"].items():
                            if key not in ['analysisDate', 'fileHash']:
                                print(f"   {key}: {value}")
                        
                        print(f"\n📦 Frontend Analysis Data:")
                        for key in ['duplicateRules', 'shadowedRules', 'unusedRules', 'overlappingRules', 'unusedObjects']:
                            count = len(frontend_data[key])
                            print(f"   {key}: {count} items")
                        
                        # Step 4: Check if frontend would display correctly
                        print(f"\n🎯 Step 4: Frontend Display Check")
                        
                        expected_display = {
                            "Dashboard": {
                                "Total Rules": frontend_data["summary"]["totalRules"],
                                "Total Objects": frontend_data["summary"]["totalObjects"],
                                "Unused Objects": frontend_data["summary"]["unusedObjects"],
                                "Used Objects": frontend_data["summary"]["totalObjects"] - frontend_data["summary"]["unusedObjects"]
                            },
                            "Analysis Tabs": {
                                "Duplicate Rules": len(frontend_data["duplicateRules"]),
                                "Shadowed Rules": len(frontend_data["shadowedRules"]),
                                "Unused Rules": len(frontend_data["unusedRules"]),
                                "Overlapping Rules": len(frontend_data["overlappingRules"]),
                                "Unused Objects": len(frontend_data["unusedObjects"])
                            }
                        }
                        
                        print(f"📱 What Frontend Should Display:")
                        print(f"   Dashboard:")
                        for key, value in expected_display["Dashboard"].items():
                            print(f"      {key}: {value}")
                        
                        print(f"   Analysis Tabs:")
                        for key, value in expected_display["Analysis Tabs"].items():
                            print(f"      {key}: {value}")
                        
                        # Step 5: Verify data completeness
                        print(f"\n✅ Step 5: Data Completeness Check")
                        
                        issues = []
                        
                        if frontend_data["summary"]["totalRules"] == 0:
                            issues.append("No rules found - frontend will show empty rules")
                        
                        if frontend_data["summary"]["totalObjects"] == 0:
                            issues.append("No objects found - frontend will show empty objects")
                        
                        if len(frontend_data["unusedObjects"]) == 0:
                            issues.append("No unused objects - frontend unused objects tab will be empty")
                        
                        if not issues:
                            print(f"   ✅ All data present - frontend should display correctly")
                            
                            # Show what user should see
                            print(f"\n🎉 SUCCESS! Frontend should show:")
                            print(f"   📊 Dashboard: {frontend_data['summary']['totalRules']} rules, {frontend_data['summary']['totalObjects']} objects")
                            print(f"   📦 Unused Objects Tab: {len(frontend_data['unusedObjects'])} unused objects")
                            print(f"   📋 Analysis complete with all categories populated")
                            
                            return True
                        else:
                            print(f"   ❌ Issues found:")
                            for issue in issues:
                                print(f"      - {issue}")
                            return False
                    else:
                        print(f"❌ No 'data' key in analysis response")
                        return False
                else:
                    print(f"❌ Analysis request failed: {analysis_response.status_code}")
                    print(f"   Response: {analysis_response.text}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_frontend_integration()
    
    if success:
        print(f"\n🚀 FRONTEND INTEGRATION IS WORKING!")
        print(f"   The backend is providing all the data the frontend needs")
        print(f"   If frontend is not showing data, the issue is in the frontend code")
        print(f"   Check browser console for JavaScript errors")
        print(f"   Verify FileUpload.tsx is calling the analysis endpoint correctly")
    else:
        print(f"\n💥 FRONTEND INTEGRATION HAS ISSUES!")
        print(f"   The backend is not providing complete data to the frontend")
        print(f"   Need to fix the backend API responses")
