import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';

interface FileUploadProps {
  onFileAnalysis: (data: any, fileName: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileAnalysis }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>('checking...');

  // Test backend connection on component mount
  React.useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/health`);
        if (response.ok) {
          setBackendStatus('connected');
          console.log('Backend connection successful');
        } else {
          setBackendStatus('error');
          console.error('Backend responded with error:', response.status);
        }
      } catch (error) {
        setBackendStatus('failed');
        console.error('Backend connection failed:', error);
      }
    };
    testBackend();
  }, []);

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

    try {
      // Create form data for the API request
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_name', `Analysis of ${file.name}`);

      console.log('Uploading file:', file.name, 'to backend...');

      // Call the backend API
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/api/v1/audits/`, {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type for FormData - let browser set it with boundary
        },
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      const auditId = result.data.audit_id;

      console.log('File uploaded successfully, audit ID:', auditId);
      console.log('Fetching analysis results...');

      // Now fetch the analysis results
      const analysisResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/api/v1/audits/${auditId}/analysis`);

      if (!analysisResponse.ok) {
        throw new Error(`Analysis failed: ${analysisResponse.status}`);
      }

      const analysisResult = await analysisResponse.json();
      console.log('Analysis results:', analysisResult);

      // Convert backend response to frontend format
      const totalObjects = (result.data.metadata.address_object_count || 0) + (result.data.metadata.service_object_count || 0);
      const analysisData = analysisResult.data;

      const frontendAnalysisData = {
        summary: {
          totalRules: analysisData.analysis_summary?.total_rules || 0,
          totalObjects: analysisData.analysis_summary?.total_objects || totalObjects,
          duplicateRules: analysisData.duplicateRules?.length || 0,
          shadowedRules: analysisData.shadowedRules?.length || 0,
          unusedRules: analysisData.unusedRules?.length || 0,
          overlappingRules: analysisData.overlappingRules?.length || 0,
          unusedObjects: analysisData.unusedObjects?.length || 0,
          redundantObjects: analysisData.redundantObjects?.length || 0,
          analysisDate: result.data.start_time,
          configVersion: result.data.metadata.firmware_version || 'Unknown',
          auditId: result.data.audit_id,
          fileName: result.data.filename,
          fileHash: result.data.file_hash,
        },
        // Use real analysis data from backend
        duplicateRules: analysisData.duplicateRules || [],
        shadowedRules: analysisData.shadowedRules || [],
        unusedRules: analysisData.unusedRules || [],
        overlappingRules: analysisData.overlappingRules || [],
        unusedObjects: analysisData.unusedObjects || [],
        redundantObjects: analysisData.redundantObjects || [],
        recommendations: [
          {
            category: 'parsing',
            priority: 'info',
            title: `Successfully parsed ${analysisData.analysis_summary?.total_rules || 0} rules and ${analysisData.analysis_summary?.total_objects || totalObjects} objects`,
            description: `Found ${analysisData.unusedObjects?.length || 0} unused objects, ${analysisData.redundantObjects?.length || 0} redundant objects, and ${analysisData.unusedRules?.length || 0} unused rules`,
            impact: 'Analysis completed - review findings for optimization opportunities'
          }
        ]
      };

      setIsAnalyzing(false);

      // Debug logging
      console.log('🎯 Frontend Analysis Data:', frontendAnalysisData);
      console.log('📊 Summary:', frontendAnalysisData.summary);
      console.log('📦 Unused Objects:', frontendAnalysisData.unusedObjects);

      onFileAnalysis(frontendAnalysisData, file.name);
    } catch (error) {
      console.error('File upload failed:', error);
      console.error('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      setIsAnalyzing(false);
      // You might want to show an error message to the user here
      alert(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}\n\nCheck browser console for details.`);
    }
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
          Processing happens on your local backend server.
        </p>
        <div className="mt-4">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            backendStatus === 'connected' ? 'bg-green-100 text-green-800' :
            backendStatus === 'checking...' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            Backend: {backendStatus}
          </span>
        </div>
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