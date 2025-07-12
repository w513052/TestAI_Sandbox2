#!/usr/bin/env python3
"""
Create a large XML test file to test streaming XML parsing functionality.
"""

def create_large_xml_file(filename: str, num_rules: int = 1000, num_objects: int = 500):
    """
    Create a large XML configuration file for testing streaming parser.
    
    Args:
        filename: Output filename
        num_rules: Number of rules to generate
        num_objects: Number of objects to generate
    """
    
    print(f"Creating large XML file: {filename}")
    print(f"  Rules: {num_rules}")
    print(f"  Objects: {num_objects}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        # XML header
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<config version="10.1.0" urldb="paloaltonetworks">\n')
        f.write('  <devices>\n')
        f.write('    <entry name="localhost.localdomain">\n')
        f.write('      <deviceconfig>\n')
        f.write('        <system>\n')
        f.write('          <version>10.1.0</version>\n')
        f.write('          <hostname>PA-VM-LARGE</hostname>\n')
        f.write('        </system>\n')
        f.write('      </deviceconfig>\n')
        f.write('      <vsys>\n')
        f.write('        <entry name="vsys1">\n')
        
        # Generate address objects
        f.write('          <address>\n')
        for i in range(num_objects // 2):
            f.write(f'            <entry name="Server-{i:04d}">\n')
            f.write(f'              <ip-netmask>192.168.{i // 254}.{i % 254 + 1}/32</ip-netmask>\n')
            f.write('            </entry>\n')
        f.write('          </address>\n')
        
        # Generate service objects
        f.write('          <service>\n')
        for i in range(num_objects // 2):
            port = 8000 + (i % 1000)
            f.write(f'            <entry name="Service-{i:04d}">\n')
            f.write('              <protocol>\n')
            f.write('                <tcp>\n')
            f.write(f'                  <port>{port}</port>\n')
            f.write('                </tcp>\n')
            f.write('              </protocol>\n')
            f.write('            </entry>\n')
        f.write('          </service>\n')
        
        # Generate security rules
        f.write('          <rulebase>\n')
        f.write('            <security>\n')
        f.write('              <rules>\n')
        
        for i in range(num_rules):
            src_obj = f"Server-{i % (num_objects // 2):04d}"
            dst_obj = f"Server-{(i + 1) % (num_objects // 2):04d}"
            svc_obj = f"Service-{i % (num_objects // 2):04d}"
            
            f.write(f'                <entry name="Rule-{i:04d}">\n')
            f.write('                  <from>\n')
            f.write('                    <member>trust</member>\n')
            f.write('                  </from>\n')
            f.write('                  <to>\n')
            f.write('                    <member>untrust</member>\n')
            f.write('                  </to>\n')
            f.write('                  <source>\n')
            f.write(f'                    <member>{src_obj}</member>\n')
            f.write('                  </source>\n')
            f.write('                  <destination>\n')
            f.write(f'                    <member>{dst_obj}</member>\n')
            f.write('                  </destination>\n')
            f.write('                  <service>\n')
            f.write(f'                    <member>{svc_obj}</member>\n')
            f.write('                  </service>\n')
            f.write('                  <action>allow</action>\n')
            
            # Make some rules disabled for testing
            if i % 10 == 0:
                f.write('                  <disabled>yes</disabled>\n')
                
            f.write('                </entry>\n')
        
        f.write('              </rules>\n')
        f.write('            </security>\n')
        f.write('          </rulebase>\n')
        f.write('        </entry>\n')
        f.write('      </vsys>\n')
        f.write('    </entry>\n')
        f.write('  </devices>\n')
        f.write('</config>\n')
    
    # Get file size
    import os
    file_size = os.path.getsize(filename)
    print(f"✅ Created {filename} ({file_size / 1024 / 1024:.1f}MB)")
    
    return filename, file_size

if __name__ == "__main__":
    # Create a large file (>5MB) to trigger streaming parser
    large_file, size = create_large_xml_file("large_test_config.xml", num_rules=2000, num_objects=1000)
    
    # Create a small file (<5MB) to use regular parser
    small_file, size = create_large_xml_file("small_test_config.xml", num_rules=50, num_objects=25)
    
    print(f"\n🎯 Test files created:")
    print(f"  Large file: {large_file} ({size / 1024 / 1024:.1f}MB) - will use streaming parser")
    print(f"  Small file: {small_file} ({size / 1024:.1f}KB) - will use regular parser")
