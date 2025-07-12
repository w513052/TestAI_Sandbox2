import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Clock, Target, TrendingDown, TrendingUp, Zap } from 'lucide-react';

interface DashboardProps {
  data: any;
  fileName: string;
}

const Dashboard: React.FC<DashboardProps> = ({ data, fileName }) => {
  const { summary, recommendations } = data;

  const metrics = [
    {
      title: 'Total Rules',
      value: summary.totalRules.toLocaleString(),
      icon: Shield,
      color: 'blue',
      description: 'Total firewall rules analyzed'
    },
    {
      title: 'Total Objects',
      value: summary.totalObjects?.toLocaleString() || '0',
      icon: Target,
      color: 'green',
      description: 'Total address and service objects'
    },
    {
      title: 'Duplicate Rules',
      value: summary.duplicateRules,
      icon: AlertTriangle,
      color: 'red',
      description: 'Rules with identical configurations'
    },
    {
      title: 'Shadowed Rules',
      value: summary.shadowedRules,
      icon: Clock,
      color: 'yellow',
      description: 'Rules blocked by higher precedence rules'
    },
    {
      title: 'Unused Rules',
      value: summary.unusedRules,
      icon: TrendingDown,
      color: 'orange',
      description: 'Rules with no traffic matches'
    },
    {
      title: 'Overlapping Rules',
      value: summary.overlappingRules,
      icon: TrendingUp,
      color: 'purple',
      description: 'Rules with overlapping traffic scope'
    },
    {
      title: 'Unused Objects',
      value: summary.unusedObjects,
      icon: Zap,
      color: 'gray',
      description: 'Unreferenced address/service objects'
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-50 border-blue-200',
      red: 'text-red-600 bg-red-50 border-red-200',
      yellow: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      orange: 'text-orange-600 bg-orange-50 border-orange-200',
      purple: 'text-purple-600 bg-purple-50 border-purple-200',
      gray: 'text-gray-600 bg-gray-50 border-gray-200',
      green: 'text-green-600 bg-green-50 border-green-200',
    };
    return colors[color as keyof typeof colors] || colors.gray;
  };

  const getPriorityClasses = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const efficiencyScore = Math.round(
    ((summary.totalRules - summary.duplicateRules - summary.shadowedRules - summary.unusedRules) / summary.totalRules) * 100
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Analysis Dashboard</h2>
            <p className="text-gray-600 mt-1">Configuration: {fileName}</p>
            <p className="text-sm text-gray-500">
              Analyzed on {new Date(summary.analysisDate).toLocaleDateString()} • 
              PAN-OS Version {summary.configVersion}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-900">{efficiencyScore}%</div>
            <div className="text-sm text-gray-600">Policy Efficiency</div>
            <div className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${
              efficiencyScore >= 80 ? 'bg-green-100 text-green-800' :
              efficiencyScore >= 60 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {efficiencyScore >= 80 ? 'Excellent' : efficiencyScore >= 60 ? 'Good' : 'Needs Attention'}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div key={index} className={`border rounded-lg p-6 ${getColorClasses(metric.color)}`}>
              <div className="flex items-center justify-between mb-3">
                <Icon className="h-8 w-8" />
                <div className="text-2xl font-bold">{metric.value}</div>
              </div>
              <h3 className="font-semibold mb-1">{metric.title}</h3>
              <p className="text-sm opacity-80">{metric.description}</p>
            </div>
          );
        })}
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Priority Recommendations</h3>
          <p className="text-gray-600 mt-1">Actionable steps to optimize your firewall policy</p>
        </div>
        <div className="p-6 space-y-4">
          {recommendations.map((rec: any, index: number) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityClasses(rec.priority)}`}>
                    {rec.priority.toUpperCase()}
                  </span>
                  <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                </div>
                <span className="text-sm text-gray-500 capitalize">{rec.category.replace('_', ' ')}</span>
              </div>
              <p className="text-gray-700 mb-2">{rec.description}</p>
              <p className="text-sm text-gray-600">
                <strong>Impact:</strong> {rec.impact}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Summary */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Rule Health Overview</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Effective Rules</span>
              <span className="font-semibold text-green-600">
                {(summary.totalRules - summary.duplicateRules - summary.shadowedRules - summary.unusedRules).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Issues Identified</span>
              <span className="font-semibold text-red-600">
                {(summary.duplicateRules + summary.shadowedRules + summary.unusedRules + summary.overlappingRules).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Potential Savings</span>
              <span className="font-semibold text-blue-600">
                {Math.round(((summary.duplicateRules + summary.unusedRules) / summary.totalRules) * 100)}% rule reduction
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Object Cleanup Potential</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Unused Objects</span>
              <span className="font-semibold text-orange-600">{summary.unusedObjects}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Redundant Objects</span>
              <span className="font-semibold text-purple-600">{summary.redundantObjects}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Total Objects to Review</span>
              <span className="font-semibold text-gray-900">{summary.unusedObjects + summary.redundantObjects}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;