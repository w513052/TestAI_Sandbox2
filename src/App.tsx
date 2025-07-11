import React, { useState } from 'react';
import { Shield, Upload, FileText, AlertTriangle, CheckCircle, XCircle, BarChart3, Download, Settings, Filter } from 'lucide-react';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import AnalysisResults from './components/AnalysisResults';
import ReportGenerator from './components/ReportGenerator';

function App() {
  const [currentView, setCurrentView] = useState<'upload' | 'dashboard' | 'results' | 'reports'>('upload');
  const [analysisData, setAnalysisData] = useState(null);
  const [fileName, setFileName] = useState('');

  const handleFileAnalysis = (data: any, name: string) => {
    setAnalysisData(data);
    setFileName(name);
    setCurrentView('dashboard');
  };

  const navigation = [
    { id: 'upload', label: 'Upload Config', icon: Upload },
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, disabled: !analysisData },
    { id: 'results', label: 'Analysis Results', icon: AlertTriangle, disabled: !analysisData },
    { id: 'reports', label: 'Generate Reports', icon: FileText, disabled: !analysisData },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-700" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Firewall Policy Optimizer</h1>
                <p className="text-sm text-gray-500">Palo Alto Configuration Analysis Tool</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Privacy-First • Local Processing</span>
              <div className="h-6 w-6 bg-green-500 rounded-full flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation */}
        <nav className="mb-8">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => !item.disabled && setCurrentView(item.id as any)}
                  disabled={item.disabled}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                    currentView === item.id
                      ? 'bg-white text-blue-700 shadow-sm'
                      : item.disabled
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Main Content */}
        <main>
          {currentView === 'upload' && (
            <FileUpload onFileAnalysis={handleFileAnalysis} />
          )}
          {currentView === 'dashboard' && analysisData && (
            <Dashboard data={analysisData} fileName={fileName} />
          )}
          {currentView === 'results' && analysisData && (
            <AnalysisResults data={analysisData} />
          )}
          {currentView === 'reports' && analysisData && (
            <ReportGenerator data={analysisData} fileName={fileName} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;