import React, { useState } from 'react';
import { FileText, Download, Mail, Settings, Calendar, User, Building } from 'lucide-react';

interface ReportGeneratorProps {
  data: any;
  fileName: string;
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ data, fileName }) => {
  const [reportFormat, setReportFormat] = useState('pdf');
  const [includeDetails, setIncludeDetails] = useState(true);
  const [includeRecommendations, setIncludeRecommendations] = useState(true);
  const [includeCharts, setIncludeCharts] = useState(true);
  const [reportTitle, setReportTitle] = useState('Firewall Policy Analysis Report');
  const [companyName, setCompanyName] = useState('');
  const [auditorName, setAuditorName] = useState('');
  const [clientName, setClientName] = useState('');

  const reportFormats = [
    { id: 'pdf', label: 'PDF Report', description: 'Professional report with charts and formatting' },
    { id: 'csv', label: 'CSV Data', description: 'Raw data for spreadsheet analysis' },
    { id: 'json', label: 'JSON Export', description: 'Technical data format for integrations' },
    { id: 'executive', label: 'Executive Summary', description: 'High-level overview for stakeholders' }
  ];

  const generateReport = () => {
    // In a real implementation, this would generate the actual report
    const reportData = {
      format: reportFormat,
      title: reportTitle,
      company: companyName,
      auditor: auditorName,
      client: clientName,
      fileName: fileName,
      analysisData: data,
      options: {
        includeDetails,
        includeRecommendations,
        includeCharts
      },
      generatedAt: new Date().toISOString()
    };

    // Simulate file download
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `firewall-analysis-${reportFormat}-${Date.now()}.${reportFormat === 'json' ? 'json' : reportFormat === 'csv' ? 'csv' : 'pdf'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate Analysis Report</h2>
        <p className="text-gray-600">Create professional reports for stakeholders and compliance documentation</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Report Configuration */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Configuration</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Report Title</label>
                <input
                  type="text"
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Company/Organization</label>
                  <input
                    type="text"
                    placeholder="Your Company"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Auditor Name</label>
                  <input
                    type="text"
                    placeholder="Your Name"
                    value={auditorName}
                    onChange={(e) => setAuditorName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Client/Project Name</label>
                <input
                  type="text"
                  placeholder="Client or Project Name (optional)"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Report Options */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Options</h3>
            
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeDetails}
                  onChange={(e) => setIncludeDetails(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-3 text-sm text-gray-700">Include detailed rule analysis</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeRecommendations}
                  onChange={(e) => setIncludeRecommendations(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-3 text-sm text-gray-700">Include optimization recommendations</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeCharts}
                  onChange={(e) => setIncludeCharts(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-3 text-sm text-gray-700">Include charts and visualizations</span>
              </label>
            </div>
          </div>
        </div>

        {/* Format Selection */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Format</h3>
            
            <div className="space-y-3">
              {reportFormats.map((format) => (
                <label key={format.id} className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="reportFormat"
                    value={format.id}
                    checked={reportFormat === format.id}
                    onChange={(e) => setReportFormat(e.target.value)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{format.label}</div>
                    <div className="text-sm text-gray-500">{format.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Report Summary */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Summary</h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Configuration File:</span>
                <span className="font-medium text-gray-900">{fileName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Rules Analyzed:</span>
                <span className="font-medium text-gray-900">{data.summary.totalRules.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Issues Identified:</span>
                <span className="font-medium text-red-600">
                  {(data.summary.duplicateRules + data.summary.shadowedRules + data.summary.unusedRules + data.summary.overlappingRules).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Recommendations:</span>
                <span className="font-medium text-blue-600">{data.recommendations.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Analysis Date:</span>
                <span className="font-medium text-gray-900">
                  {new Date(data.summary.analysisDate).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateReport}
            className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <Download className="h-5 w-5" />
            <span>Generate {reportFormats.find(f => f.id === reportFormat)?.label}</span>
          </button>
        </div>
      </div>

      {/* Report Preview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Report Preview</h3>
          <p className="text-gray-600 mt-1">Preview of your report content and structure</p>
        </div>
        <div className="p-6">
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8">
            <div className="text-center space-y-4">
              <FileText className="h-12 w-12 text-gray-400 mx-auto" />
              <div>
                <h4 className="text-lg font-semibold text-gray-900">{reportTitle}</h4>
                {companyName && <p className="text-gray-600">{companyName}</p>}
                <p className="text-sm text-gray-500 mt-2">
                  Analysis of {fileName} • {new Date().toLocaleDateString()}
                </p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{data.summary.totalRules.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">Total Rules</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{data.summary.duplicateRules}</div>
                  <div className="text-xs text-gray-500">Duplicates</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{data.summary.shadowedRules}</div>
                  <div className="text-xs text-gray-500">Shadowed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{data.summary.unusedRules}</div>
                  <div className="text-xs text-gray-500">Unused</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;