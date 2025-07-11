import React, { useState } from 'react';
import { Search, Filter, Download, AlertTriangle, XCircle, Clock, Target, Zap } from 'lucide-react';

interface AnalysisResultsProps {
  data: any;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState('duplicates');
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');

  const tabs = [
    { id: 'duplicates', label: 'Duplicate Rules', icon: XCircle, count: data.duplicateRules.length, color: 'red' },
    { id: 'shadowed', label: 'Shadowed Rules', icon: Clock, count: data.shadowedRules.length, color: 'yellow' },
    { id: 'unused', label: 'Unused Rules', icon: AlertTriangle, count: data.unusedRules.length, color: 'orange' },
    { id: 'overlapping', label: 'Overlapping Rules', icon: Target, count: data.overlappingRules.length, color: 'purple' },
    { id: 'objects', label: 'Unused Objects', icon: Zap, count: data.unusedObjects.length, color: 'gray' }
  ];

  const getTabColorClasses = (color: string, isActive: boolean) => {
    const colors = {
      red: isActive ? 'border-red-500 text-red-600' : 'border-transparent text-gray-500 hover:text-red-600',
      yellow: isActive ? 'border-yellow-500 text-yellow-600' : 'border-transparent text-gray-500 hover:text-yellow-600',
      orange: isActive ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-500 hover:text-orange-600',
      purple: isActive ? 'border-purple-500 text-purple-600' : 'border-transparent text-gray-500 hover:text-purple-600',
      gray: isActive ? 'border-gray-500 text-gray-600' : 'border-transparent text-gray-500 hover:text-gray-600'
    };
    return colors[color as keyof typeof colors] || colors.gray;
  };

  const getSeverityBadge = (severity: string) => {
    const classes = {
      high: 'bg-red-100 text-red-800 border-red-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-green-100 text-green-800 border-green-200'
    };
    return classes[severity as keyof typeof classes] || classes.low;
  };

  const renderRuleTable = (rules: any[], type: string) => {
    const filteredRules = rules.filter(rule => {
      const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          rule.source.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          rule.destination.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSeverity = severityFilter === 'all' || rule.severity === severityFilter;
      return matchesSearch && matchesSeverity;
    });

    return (
      <div className="space-y-4">
        {filteredRules.map((rule, index) => (
          <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <h4 className="text-lg font-semibold text-gray-900">{rule.name}</h4>
                <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getSeverityBadge(rule.severity)}`}>
                  {rule.severity.toUpperCase()}
                </span>
              </div>
              <span className="text-sm text-gray-500">Rule ID: {rule.id}</span>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">From Zone</label>
                <p className="mt-1 text-sm text-gray-900">{rule.fromZone}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">To Zone</label>
                <p className="mt-1 text-sm text-gray-900">{rule.toZone}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Source</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{rule.source}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Destination</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">{rule.destination}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Service</label>
                <p className="mt-1 text-sm text-gray-900">{rule.service}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Action</label>
                <p className={`mt-1 text-sm font-medium ${rule.action === 'allow' ? 'text-green-600' : 'text-red-600'}`}>
                  {rule.action.toUpperCase()}
                </p>
              </div>
              {type === 'duplicates' && rule.duplicateOf && (
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Duplicate Of</label>
                  <p className="mt-1 text-sm text-blue-600">{rule.duplicateOf}</p>
                </div>
              )}
              {type === 'shadowed' && rule.shadowedBy && (
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Shadowed By</label>
                  <p className="mt-1 text-sm text-blue-600">{rule.shadowedBy}</p>
                </div>
              )}
              {type === 'overlapping' && rule.overlapsWith && (
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Overlaps With</label>
                  <p className="mt-1 text-sm text-blue-600">{rule.overlapsWith.join(', ')}</p>
                </div>
              )}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <label className="block text-xs font-medium text-blue-800 uppercase tracking-wide mb-1">Recommendation</label>
              <p className="text-sm text-blue-900">{rule.recommendation}</p>
            </div>
          </div>
        ))}

        {filteredRules.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No rules match the current filters.</p>
          </div>
        )}
      </div>
    );
  };

  const renderObjectsTable = () => {
    const filteredObjects = data.unusedObjects.filter((obj: any) => {
      const matchesSearch = obj.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          obj.value.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSeverity = severityFilter === 'all' || obj.severity === severityFilter;
      return matchesSearch && matchesSeverity;
    });

    return (
      <div className="space-y-4">
        {filteredObjects.map((obj: any, index: number) => (
          <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <h4 className="text-lg font-semibold text-gray-900">{obj.name}</h4>
                <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getSeverityBadge(obj.severity)}`}>
                  {obj.severity.toUpperCase()}
                </span>
                <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                  {obj.type.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">Value</label>
              <p className="mt-1 text-sm text-gray-900 font-mono">{obj.value}</p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <label className="block text-xs font-medium text-blue-800 uppercase tracking-wide mb-1">Recommendation</label>
              <p className="text-sm text-blue-900">{obj.recommendation}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const getActiveData = () => {
    switch (activeTab) {
      case 'duplicates':
        return data.duplicateRules;
      case 'shadowed':
        return data.shadowedRules;
      case 'unused':
        return data.unusedRules;
      case 'overlapping':
        return data.overlappingRules;
      case 'objects':
        return data.unusedObjects;
      default:
        return [];
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Detailed Analysis Results</h2>
        
        {/* Filters */}
        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search rules by name, source, or destination..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Severities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${getTabColorClasses(tab.color, isActive)}`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${isActive ? 'bg-current bg-opacity-10' : 'bg-gray-100 text-gray-600'}`}>
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'objects' ? renderObjectsTable() : renderRuleTable(getActiveData(), activeTab)}
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;