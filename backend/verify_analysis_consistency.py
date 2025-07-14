#!/usr/bin/env python3
"""
Verify that SET and XML formats are producing consistent analysis results.
"""

import sqlite3
import json
import urllib.request
import urllib.error

def get_analysis_data(audit_id):
    """Get analysis data from the API."""
    try:
        url = f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis'
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data.get('data', {})
    except Exception as e:
        print(f"❌ Error getting analysis for audit {audit_id}: {str(e)}")
        return None

def verify_analysis_consistency():
    """Verify analysis consistency between SET and XML formats."""
    
    print("🔍 VERIFYING ANALYSIS CONSISTENCY: SET vs XML")
    print("=" * 55)
    
    try:
        conn = sqlite3.connect('firewall_tool.db')
        cursor = conn.cursor()
        
        # Get the most recent SET and XML audits
        cursor.execute('''
            SELECT id, filename 
            FROM audit_sessions 
            WHERE filename LIKE '%.txt'
            ORDER BY id DESC 
            LIMIT 1
        ''')
        set_audit = cursor.fetchone()
        
        cursor.execute('''
            SELECT id, filename 
            FROM audit_sessions 
            WHERE filename LIKE '%.xml'
            ORDER BY id DESC 
            LIMIT 1
        ''')
        xml_audit = cursor.fetchone()
        
        if not set_audit or not xml_audit:
            print("❌ Could not find both SET and XML audits")
            return
        
        set_id, set_filename = set_audit
        xml_id, xml_filename = xml_audit
        
        print(f"📋 Comparing Analysis Results:")
        print(f"   SET: Audit {set_id} - {set_filename}")
        print(f"   XML: Audit {xml_id} - {xml_filename}")
        
        # Get database stats for context
        get_database_stats(cursor, set_id, "SET", xml_id, "XML")
        
        # Get analysis results from API
        set_analysis = get_analysis_data(set_id)
        xml_analysis = get_analysis_data(xml_id)
        
        if not set_analysis or not xml_analysis:
            print("❌ Could not get analysis data from API")
            return
        
        # Compare analysis results
        compare_analysis_results(set_analysis, "SET", xml_analysis, "XML")
        
        # Check for format-specific issues
        check_format_specific_issues(set_analysis, "SET", xml_analysis, "XML")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def get_database_stats(cursor, set_id, set_name, xml_id, xml_name):
    """Get database statistics for context."""
    
    print(f"\n📊 Database Statistics:")
    
    for audit_id, format_name in [(set_id, set_name), (xml_id, xml_name)]:
        # Count objects and rules
        cursor.execute('SELECT COUNT(*) FROM object_definitions WHERE audit_id = ?', (audit_id,))
        obj_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ?', (audit_id,))
        rule_count = cursor.fetchone()[0]
        
        # Count disabled rules
        cursor.execute('SELECT COUNT(*) FROM firewall_rules WHERE audit_id = ? AND is_disabled = 1', (audit_id,))
        disabled_count = cursor.fetchone()[0]
        
        print(f"   {format_name}: {obj_count} objects, {rule_count} rules ({disabled_count} disabled)")

def compare_analysis_results(set_analysis, set_name, xml_analysis, xml_name):
    """Compare the analysis results between formats."""
    
    print(f"\n📈 Analysis Results Comparison:")
    
    # Get summaries
    set_summary = set_analysis.get('analysis_summary', {})
    xml_summary = xml_analysis.get('analysis_summary', {})
    
    # Compare key metrics
    metrics = [
        'total_objects',
        'used_objects_count', 
        'unused_objects_count',
        'redundant_objects_count',
        'total_rules'
    ]
    
    print(f"   📊 Summary Metrics:")
    for metric in metrics:
        set_val = set_summary.get(metric, 'N/A')
        xml_val = xml_summary.get(metric, 'N/A')
        print(f"      {metric}: {set_name}={set_val}, {xml_name}={xml_val}")
    
    # Compare detailed analysis categories
    categories = [
        ('unusedObjects', 'Unused Objects'),
        ('redundantObjects', 'Redundant Objects'),
        ('unusedRules', 'Unused Rules'),
        ('duplicateRules', 'Duplicate Rules'),
        ('shadowedRules', 'Shadowed Rules'),
        ('overlappingRules', 'Overlapping Rules')
    ]
    
    print(f"\n   📋 Detailed Analysis Categories:")
    
    analysis_issues = []
    
    for category_key, category_name in categories:
        set_items = set_analysis.get(category_key, [])
        xml_items = xml_analysis.get(category_key, [])
        
        set_count = len(set_items) if set_items else 0
        xml_count = len(xml_items) if xml_items else 0
        
        # Check for expected results based on configuration
        expected_results = get_expected_results(category_key)
        
        set_status = check_category_status(set_count, expected_results.get('set', 0))
        xml_status = check_category_status(xml_count, expected_results.get('xml', 0))
        
        print(f"      {category_name}: {set_name}={set_count} {set_status}, {xml_name}={xml_count} {xml_status}")
        
        # Track issues
        if set_status == "❌" or xml_status == "❌":
            analysis_issues.append(f"{category_name}: {set_name}={set_count}, {xml_name}={xml_count}")
    
    return analysis_issues

def get_expected_results(category_key):
    """Get expected results for each category based on known configurations."""
    
    # Based on the configurations we saw:
    # SET: 8 objects (2 duplicates), 8 rules (2 duplicates, 1 unused)
    # XML: 8 objects (2 duplicates), 8 rules (various patterns)
    
    expectations = {
        'unusedObjects': {'set': 1, 'xml': 1},  # Both should have unused objects
        'redundantObjects': {'set': 2, 'xml': 2},  # Both have duplicate objects
        'unusedRules': {'set': 1, 'xml': 0},  # SET has unused rule, XML may not
        'duplicateRules': {'set': 2, 'xml': 2},  # Both should detect duplicates
        'shadowedRules': {'set': 0, 'xml': 0},  # May not have shadowed rules
        'overlappingRules': {'set': 0, 'xml': 2}  # XML might have overlapping rules
    }
    
    return expectations.get(category_key, {'set': 0, 'xml': 0})

def check_category_status(actual, expected):
    """Check if the category result matches expectations."""
    if actual == expected:
        return "✅"
    elif actual > 0 and expected > 0:
        return "🔧"  # Working but not exact
    elif actual == 0 and expected > 0:
        return "❌"  # Should detect but doesn't
    else:
        return "⚪"  # Neutral

def check_format_specific_issues(set_analysis, set_name, xml_analysis, xml_name):
    """Check for format-specific analysis issues."""
    
    print(f"\n🔧 Format-Specific Issue Analysis:")
    
    # Check SET format issues
    set_issues = []
    set_summary = set_analysis.get('analysis_summary', {})
    
    if set_summary.get('unused_objects_count', 0) == 0:
        set_issues.append("Not detecting unused objects")
    if len(set_analysis.get('duplicateRules', [])) == 0:
        set_issues.append("Not detecting duplicate rules")
    if len(set_analysis.get('overlappingRules', [])) == 0:
        set_issues.append("Not detecting overlapping rules")
    
    # Check XML format issues  
    xml_issues = []
    xml_summary = xml_analysis.get('analysis_summary', {})
    
    if len(xml_analysis.get('shadowedRules', [])) == 0:
        xml_issues.append("Not detecting shadowed rules")
    if len(xml_analysis.get('duplicateRules', [])) == 0:
        xml_issues.append("Not detecting duplicate rules")
    
    print(f"   {set_name} Format Issues:")
    if set_issues:
        for issue in set_issues:
            print(f"      ❌ {issue}")
    else:
        print(f"      ✅ No major issues detected")
    
    print(f"   {xml_name} Format Issues:")
    if xml_issues:
        for issue in xml_issues:
            print(f"      ❌ {issue}")
    else:
        print(f"      ✅ No major issues detected")
    
    # Overall assessment
    total_issues = len(set_issues) + len(xml_issues)
    
    print(f"\n📊 Overall Assessment:")
    if total_issues == 0:
        print(f"   ✅ Both formats working well")
    elif total_issues <= 2:
        print(f"   🔧 Minor issues detected ({total_issues} issues)")
    else:
        print(f"   ❌ Significant issues detected ({total_issues} issues)")
    
    return total_issues

if __name__ == "__main__":
    print("🚀 VERIFYING ANALYSIS CONSISTENCY")
    print("=" * 60)
    
    verify_analysis_consistency()
    
    print(f"\n💡 Key Points:")
    print(f"   - Different configurations should still show consistent analysis logic")
    print(f"   - Each format should detect issues appropriate to its configuration")
    print(f"   - Analysis pipeline should work equally well for both formats")
    print(f"   - Any format-specific gaps indicate parsing or analysis issues")
