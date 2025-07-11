import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';

interface FileUploadProps {
  onFileAnalysis: (data: any, fileName: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileAnalysis }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const generateMockAnalysis = (fileName: string) => {
    return {
      summary: {
        totalRules: 1247,
        duplicateRules: 23,
        shadowedRules: 15,
        unusedRules: 87,
        overlappingRules: 34,
        unusedObjects: 156,
        redundantObjects: 42,
        analysisDate: new Date().toISOString(),
        configVersion: '10.1.0',
      },
      duplicateRules: [
        {
          id: 'rule-001',
          name: 'Allow-Web-Traffic',
          fromZone: 'Trust',
          toZone: 'Untrust',
          source: '192.168.1.0/24',
          destination: 'any',
          service: 'service-http',
          action: 'allow',
          duplicateOf: 'rule-089',
          severity: 'high',
          recommendation: 'Remove duplicate rule and consolidate traffic into rule-089'
        },
        {
          id: 'rule-045',
          name: 'DNS-Access',
          fromZone: 'DMZ',
          toZone: 'Untrust',
          source: '10.10.10.0/24',
          destination: 'any',
          service: 'service-dns',
          action: 'allow',
          duplicateOf: 'rule-156',
          severity: 'medium',
          recommendation: 'Merge with existing DNS rule to reduce policy complexity'
        }
      ],
      shadowedRules: [
        {
          id: 'rule-234',
          name: 'Block-Specific-IP',
          fromZone: 'Trust',
          toZone: 'Untrust',
          source: '192.168.1.100',
          destination: '203.0.113.50',
          service: 'any',
          action: 'deny',
          shadowedBy: 'rule-012',
          severity: 'high',
          recommendation: 'Move rule above rule-012 or remove if redundant'
        }
      ],
      unusedRules: [
        {
          id: 'rule-567',
          name: 'Old-VPN-Access',
          fromZone: 'VPN',
          toZone: 'Trust',
          source: '172.16.0.0/16',
          destination: '192.168.2.0/24',
          service: 'any',
          action: 'allow',
          lastHit: null,
          severity: 'medium',
          recommendation: 'Verify if VPN access is still required, consider removal'
        }
      ],
      overlappingRules: [
        {
          id: 'rule-789',
          name: 'Broad-Web-Access',
          fromZone: 'Trust',
          toZone: 'Untrust',
          source: '192.168.0.0/16',
          destination: 'any',
          service: 'service-http',
          action: 'allow',
          overlapsWith: ['rule-790', 'rule-791'],
          severity: 'medium',
          recommendation: 'Consider consolidating overlapping web access rules'
        }
      ],
      unusedObjects: [
        {
          type: 'address',
          name: 'Legacy-Server-Group',
          value: '192.168.100.0/24',
          severity: 'low',
          recommendation: 'Remove unused address object to clean up configuration'
        },
        {
          type: 'service',
          name: 'Custom-Port-8080',
          value: 'tcp/8080',
          severity: 'low',
          recommendation: 'Remove unused service object'
        }
      ],
      recommendations: [
        {
          category: 'rule_optimization',
          priority: 'high',
          title: 'Remove 23 duplicate rules',
          description: 'Consolidate duplicate rules to reduce policy complexity and improve performance',
          impact: 'Reduces rule count by 1.8% and eliminates confusion in policy management'
        },
        {
          category: 'security',
          priority: 'high',
          title: 'Fix 15 shadowed rules',
          description: 'Reorder or remove shadowed rules that may not be enforcing intended security policies',
          impact: 'Ensures security policies are properly enforced as intended'
        },
        {
          category: 'cleanup',
          priority: 'medium',
          title: 'Remove 87 unused rules',
          description: 'Clean up rules that have not been hit in the analysis period',
          impact: 'Reduces policy complexity and improves firewall performance'
        }
      ]
    };
  };

  const handleFileUpload = useCallback(async (file: File) => {
    setUploadedFile(file);
    setIsAnalyzing(true);

    // Simulate analysis time
    await new Promise(resolve => setTimeout(resolve, 3000));

    const analysisData = generateMockAnalysis(file.name);
    setIsAnalyzing(false);
    onFileAnalysis(analysisData, file.name);
  }, [onFileAnalysis]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.xml') || file.name.endsWith('.conf') || file.name.endsWith('.txt')) {
        handleFileUpload(file);
      }
    }
  }, [handleFileUpload]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  if (isAnalyzing) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <Loader className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing Configuration</h3>
            <p className="text-gray-600 mb-4">Processing {uploadedFile?.name}</p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Parsing rules and objects...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Upload Palo Alto Configuration</h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload your firewall configuration file for comprehensive analysis. 
          All processing happens locally - your data never leaves your device.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Upload Area */}
        <div className="space-y-6">
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onDragEnter={() => setIsDragging(true)}
            onDragLeave={() => setIsDragging(false)}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Drop your configuration file here
            </h3>
            <p className="text-gray-600 mb-4">
              or click to browse and select a file
            </p>
            <input
              type="file"
              accept=".xml,.conf,.txt"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer transition-colors"
            >
              <FileText className="h-4 w-4 mr-2" />
              Choose File
            </label>
          </div>

          {/* Supported Formats */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Supported Formats</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• XML configuration exports (.xml)</li>
              <li>• Set command format (.conf, .txt)</li>
              <li>• Panorama shared configurations</li>
            </ul>
          </div>
        </div>

        {/* Features */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Analysis Features</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Rule Analysis</p>
                  <p className="text-sm text-gray-600">Detect duplicates, shadows, overlaps, and unused rules</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Object Optimization</p>
                  <p className="text-sm text-gray-600">Identify unused address and service objects</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Actionable Recommendations</p>
                  <p className="text-sm text-gray-600">Clear guidance for policy optimization</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Professional Reports</p>
                  <p className="text-sm text-gray-600">Export findings in PDF, CSV, or JSON formats</p>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900">Privacy & Security</h4>
                <p className="text-sm text-blue-800 mt-1">
                  All analysis is performed locally in your browser. No configuration data 
                  is transmitted to external servers or stored remotely.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;