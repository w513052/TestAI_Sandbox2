#!/usr/bin/env python3
"""
Debug why set command outputs show no analysis counts and XML outputs miss shadowed/duplicate rules.
"""

import requests
import sqlite3

def debug_missing_analysis_counts():
    """Debug missing analysis counts for both set and XML formats."""
    
    print("🔍 DEBUGGING MISSING ANALYSIS COUNTS")
    print("=" * 50)
    
    try:
        # Get recent audits to compare set vs XML
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_name, filename 
            FROM audit_sessions 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        audits = cursor.fetchall()
        
        print(f"📋 Recent Audits:")
        for audit_id, session_name, filename in audits:
            file_type = "XML" if filename.endswith('.xml') else "SET"
            print(f"   {audit_id}: {filename} ({file_type})")
        
        # Test both a set format and XML format audit
        set_audit = None
        xml_audit = None
        
        for audit_id, session_name, filename in audits:
            if filename.endswith('.xml') and xml_audit is None:
                xml_audit = audit_id
            elif filename.endswith('.txt') and set_audit is None:
                set_audit = audit_id
        
        conn.close()
        
        # Test SET format analysis
        if set_audit:
            print(f"\n🔧 Testing SET Format Analysis (Audit {set_audit}):")
            test_analysis_counts(set_audit, "SET")
        
        # Test XML format analysis
        if xml_audit:
            print(f"\n📄 Testing XML Format Analysis (Audit {xml_audit}):")
            test_analysis_counts(xml_audit, "XML")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return False

def test_analysis_counts(audit_id, format_type):
    """Test analysis counts for a specific audit."""
    
    try:
        # Get analysis results
        analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()['data']
            summary = analysis_data['analysis_summary']
            
            print(f"   📊 {format_type} Analysis Summary:")
            print(f"      Total Rules: {summary.get('total_rules', 'MISSING')}")
            print(f"      Total Objects: {summary.get('total_objects', 'MISSING')}")
            print(f"      Used Objects: {summary.get('used_objects_count', 'MISSING')}")
            print(f"      Unused Objects: {summary.get('unused_objects_count', 'MISSING')}")
            print(f"      Redundant Objects: {summary.get('redundant_objects_count', 'MISSING')}")
            
            # Check detailed analysis arrays
            categories = {
                'unusedObjects': 'Unused Objects',
                'redundantObjects': 'Redundant Objects',
                'unusedRules': 'Unused Rules',
                'duplicateRules': 'Duplicate Rules',
                'shadowedRules': 'Shadowed Rules',
                'overlappingRules': 'Overlapping Rules'
            }
            
            print(f"   📋 {format_type} Detailed Analysis:")
            missing_categories = []
            empty_categories = []
            working_categories = []
            
            for key, name in categories.items():
                if key in analysis_data:
                    items = analysis_data[key]
                    count = len(items) if items else 0
                    if count > 0:
                        working_categories.append(f"{name}: {count}")
                        print(f"      ✅ {name}: {count} items")
                    else:
                        empty_categories.append(name)
                        print(f"      ⚪ {name}: 0 items")
                else:
                    missing_categories.append(name)
                    print(f"      ❌ {name}: MISSING")
            
            # Summary for this format
            print(f"   📈 {format_type} Analysis Status:")
            print(f"      Working categories: {len(working_categories)}")
            print(f"      Empty categories: {len(empty_categories)}")
            print(f"      Missing categories: {len(missing_categories)}")
            
            if missing_categories:
                print(f"      🚨 Missing: {', '.join(missing_categories)}")
            
            if format_type == "SET" and len(working_categories) == 0:
                print(f"      🚨 SET FORMAT ISSUE: No analysis categories working!")
                print(f"         This explains why set outputs show no counts")
            
            if format_type == "XML" and any("Shadowed" in cat or "Duplicate" in cat for cat in missing_categories + empty_categories):
                print(f"      🚨 XML FORMAT ISSUE: Missing shadowed/duplicate rule detection!")
            
            # Check if rule analysis is being called
            print(f"   🔍 {format_type} Rule Analysis Check:")
            
            # Get rules from database to see if analysis should find issues
            conn = sqlite3.connect('firewall_tool.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ?
            """, (audit_id,))
            rule_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ? AND is_disabled = 1
            """, (audit_id,))
            disabled_count = cursor.fetchone()[0]
            
            print(f"      Total rules in DB: {rule_count}")
            print(f"      Disabled rules in DB: {disabled_count}")
            
            if rule_count > 0 and len(working_categories) == 0:
                print(f"      🚨 ANALYSIS PIPELINE BROKEN: Rules exist but no analysis results")
            
            conn.close()
            
        else:
            print(f"   ❌ {format_type} Analysis request failed: {analysis_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ {format_type} Analysis test failed: {str(e)}")

def suggest_fixes():
    """Suggest fixes for the missing analysis counts."""
    
    print(f"\n🔧 SUGGESTED FIXES:")
    print("=" * 30)
    
    print(f"1. **SET Format Analysis Issue:**")
    print(f"   - Analysis pipeline not running for set format files")
    print(f"   - Check if rule analysis functions are being called")
    print(f"   - Verify analysis endpoint handles set format correctly")
    
    print(f"\n2. **XML Format Shadowed/Duplicate Rules Issue:**")
    print(f"   - Shadowed rule detection logic may be broken")
    print(f"   - Duplicate rule detection logic may be broken")
    print(f"   - Check rule analysis functions in rule_analysis.py")
    
    print(f"\n3. **General Analysis Pipeline Issue:**")
    print(f"   - Analysis functions may be failing silently")
    print(f"   - Error handling may be hiding exceptions")
    print(f"   - Check logs for analysis errors")
    
    print(f"\n4. **Frontend Display Issue:**")
    print(f"   - Frontend may not be receiving analysis data")
    print(f"   - Check API response structure")
    print(f"   - Verify frontend data processing")

if __name__ == "__main__":
    print("🚀 DEBUGGING MISSING ANALYSIS COUNTS")
    print("=" * 60)
    
    success = debug_missing_analysis_counts()
    
    if success:
        suggest_fixes()
        
        print(f"\n💡 SUMMARY:")
        print(f"   SET format: Missing all analysis counts except totals")
        print(f"   XML format: Missing shadowed and duplicate rules")
        print(f"   Both issues suggest analysis pipeline problems")
    else:
        print(f"\n❌ Could not debug analysis count issues")
    
    print(f"\n🎯 PRIORITY FIXES:")
    print(f"   1. Fix SET format analysis pipeline")
    print(f"   2. Fix XML shadowed/duplicate rule detection")
    print(f"   3. Ensure all analysis categories work for both formats")
