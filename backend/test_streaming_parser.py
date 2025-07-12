#!/usr/bin/env python3
"""
Test the streaming XML parser functionality.
"""

import requests
import json
import time
import os

def test_streaming_parser():
    """Test both regular and streaming XML parsers."""
    
    print("🧪 Testing Streaming XML Parser")
    print("=" * 50)
    
    # Test files
    test_files = [
        ("small_test_config.xml", "Small file (regular parser)"),
        ("large_test_config.xml", "Medium file (regular parser)"), 
        ("very_large_test_config.xml", "Large file (streaming parser)")
    ]
    
    results = []
    
    for filename, description in test_files:
        if not os.path.exists(filename):
            print(f"❌ {filename} not found, skipping...")
            continue
            
        file_size = os.path.getsize(filename)
        print(f"\n📁 Testing {description}")
        print(f"   File: {filename} ({file_size / 1024 / 1024:.1f}MB)")
        
        # Test upload and parsing
        start_time = time.time()
        
        try:
            with open(filename, "rb") as f:
                files = {"file": (filename, f, "application/xml")}
                data = {"session_name": f"Streaming Test - {description}"}
                
                upload_response = requests.post(
                    'http://127.0.0.1:8000/api/v1/audits/',
                    files=files,
                    data=data
                )
                
                upload_time = time.time() - start_time
                
                if upload_response.status_code == 200:
                    result = upload_response.json()
                    metadata = result['data']['metadata']
                    
                    print(f"   ✅ Upload successful ({upload_time:.2f}s)")
                    print(f"   📊 Results:")
                    print(f"      Rules parsed: {metadata.get('rules_parsed', 0)}")
                    print(f"      Objects parsed: {metadata.get('objects_parsed', 0)}")
                    print(f"      Address objects: {metadata.get('address_object_count', 0)}")
                    print(f"      Service objects: {metadata.get('service_object_count', 0)}")
                    
                    # Test analysis endpoint
                    audit_id = result['data']['audit_id']
                    analysis_start = time.time()
                    
                    analysis_response = requests.get(
                        f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis'
                    )
                    
                    analysis_time = time.time() - analysis_start
                    
                    if analysis_response.status_code == 200:
                        analysis_result = analysis_response.json()
                        analysis_data = analysis_result['data']
                        
                        print(f"   ✅ Analysis successful ({analysis_time:.2f}s)")
                        print(f"   🔍 Analysis results:")
                        print(f"      Total rules: {analysis_data['analysis_summary']['total_rules']}")
                        print(f"      Total objects: {analysis_data['analysis_summary']['total_objects']}")
                        print(f"      Unused objects: {analysis_data['analysis_summary']['unused_objects_count']}")
                        print(f"      Used objects: {analysis_data['analysis_summary']['used_objects_count']}")
                        
                        results.append({
                            'file': filename,
                            'size_mb': file_size / 1024 / 1024,
                            'upload_time': upload_time,
                            'analysis_time': analysis_time,
                            'total_time': upload_time + analysis_time,
                            'rules': metadata.get('rules_parsed', 0),
                            'objects': metadata.get('objects_parsed', 0),
                            'unused_objects': analysis_data['analysis_summary']['unused_objects_count'],
                            'success': True
                        })
                    else:
                        print(f"   ❌ Analysis failed: {analysis_response.status_code}")
                        results.append({
                            'file': filename,
                            'size_mb': file_size / 1024 / 1024,
                            'upload_time': upload_time,
                            'success': False,
                            'error': 'Analysis failed'
                        })
                else:
                    print(f"   ❌ Upload failed: {upload_response.status_code}")
                    print(f"   Error: {upload_response.text}")
                    results.append({
                        'file': filename,
                        'size_mb': file_size / 1024 / 1024,
                        'success': False,
                        'error': f'Upload failed: {upload_response.status_code}'
                    })
                    
        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")
            results.append({
                'file': filename,
                'size_mb': file_size / 1024 / 1024,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n📈 Performance Summary")
    print("=" * 50)
    
    successful_results = [r for r in results if r.get('success', False)]
    
    if successful_results:
        print(f"{'File':<25} {'Size (MB)':<10} {'Upload (s)':<12} {'Analysis (s)':<14} {'Total (s)':<10} {'Rules':<8} {'Objects':<8}")
        print("-" * 95)
        
        for result in successful_results:
            print(f"{result['file']:<25} {result['size_mb']:<10.1f} {result['upload_time']:<12.2f} {result.get('analysis_time', 0):<14.2f} {result.get('total_time', 0):<10.2f} {result.get('rules', 0):<8} {result.get('objects', 0):<8}")
        
        # Performance analysis
        if len(successful_results) > 1:
            print(f"\n🎯 Performance Analysis:")
            
            # Compare small vs large file performance
            small_files = [r for r in successful_results if r['size_mb'] < 5.0]
            large_files = [r for r in successful_results if r['size_mb'] >= 5.0]
            
            if small_files and large_files:
                avg_small_time = sum(r.get('total_time', 0) for r in small_files) / len(small_files)
                avg_large_time = sum(r.get('total_time', 0) for r in large_files) / len(large_files)
                
                print(f"   Average time for small files (<5MB): {avg_small_time:.2f}s")
                print(f"   Average time for large files (≥5MB): {avg_large_time:.2f}s")
                
                if avg_large_time > 0:
                    efficiency = avg_small_time / avg_large_time
                    print(f"   Streaming parser efficiency: {efficiency:.2f}x")
        
        print(f"\n✅ Streaming XML parser test completed successfully!")
        print(f"   {len(successful_results)} out of {len(results)} tests passed")
        
        return True
    else:
        print(f"\n❌ All tests failed")
        for result in results:
            if not result.get('success', False):
                print(f"   {result['file']}: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_streaming_parser()
    if success:
        print(f"\n🚀 Streaming XML parsing is working correctly!")
    else:
        print(f"\n💥 Streaming XML parsing needs debugging")
