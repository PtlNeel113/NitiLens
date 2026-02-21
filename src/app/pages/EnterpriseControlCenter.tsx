import { useState, useEffect } from 'react';
import { Zap, Shield, TrendingUp, BarChart3, Database, Activity, Bell, Languages, Cloud, Settings, Target, Globe, FileText, Loader2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { dashboardAPI } from '../services/api-enterprise';
import { useNavigate } from 'react-router';

export function EnterpriseControlCenter() {
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const data = await dashboardAPI.getOverview(token);
        setOverview(data);
      }
    } catch (error) {
      console.error('Error loading overview:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Zap className="w-8 h-8 text-blue-600" />
            Enterprise Control Center
          </h1>
          <p className="text-gray-600">
            Centralized access to all enterprise compliance governance features
          </p>
        </div>

        {/* Enterprise Summary Badges */}
        {overview && (
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <Card className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-700 font-medium">Open Cases</p>
                  <p className="text-2xl font-bold text-blue-900">{overview.remediation?.open_cases || 0}</p>
                </div>
                <Shield className="w-8 h-8 text-blue-600 opacity-50" />
              </div>
            </Card>

            <Card className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-700 font-medium">High Risk</p>
                  <p className="text-2xl font-bold text-orange-900">{overview.risk?.high_risk_anomalies || 0}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-600 opacity-50" />
              </div>
            </Card>

            <Card className="p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-700 font-medium">Active Policies</p>
                  <p className="text-2xl font-bold text-green-900">{overview.policies?.active_policies || 0}</p>
                </div>
                <FileText className="w-8 h-8 text-green-600 opacity-50" />
              </div>
            </Card>

            <Card className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-700 font-medium">Connectors</p>
                  <p className="text-2xl font-bold text-purple-900">{overview.connectors?.active_connectors || 0}</p>
                </div>
                <Database className="w-8 h-8 text-purple-600 opacity-50" />
              </div>
            </Card>
          </div>
        )}

        {/* Feature Access Grid */}
        <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
          {/* Automated Remediation */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-blue-500"
            onClick={() => navigate('/remediation')}
          >
            <Shield className="w-10 h-10 text-blue-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Automated Remediation</h3>
            <p className="text-sm text-gray-600 mb-3">
              Manage violation lifecycle from detection to resolution
            </p>
            {overview?.remediation && (
              <Badge variant="secondary" className="text-xs">
                {overview.remediation.open_cases} open cases
              </Badge>
            )}
          </Card>

          {/* Risk Intelligence */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-orange-500"
            onClick={() => navigate('/risk')}
          >
            <TrendingUp className="w-10 h-10 text-orange-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Risk Intelligence</h3>
            <p className="text-sm text-gray-600 mb-3">
              ML-powered anomaly detection and risk scoring
            </p>
            {overview?.risk && (
              <Badge variant="secondary" className="text-xs">
                {overview.risk.high_risk_anomalies} high risk
              </Badge>
            )}
          </Card>

          {/* Policy Impact Analysis */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-green-500"
            onClick={() => navigate('/policy-impact')}
          >
            <BarChart3 className="w-10 h-10 text-green-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Policy Impact</h3>
            <p className="text-sm text-gray-600 mb-3">
              Analyze impact of policy changes and versions
            </p>
            {overview?.policies && (
              <Badge variant="secondary" className="text-xs">
                {overview.policies.recent_changes} recent changes
              </Badge>
            )}
          </Card>

          {/* Multi-Policy Support */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-purple-500"
            onClick={() => navigate('/upload')}
          >
            <FileText className="w-10 h-10 text-purple-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Multi-Policy</h3>
            <p className="text-sm text-gray-600 mb-3">
              Manage multiple policies with versioning
            </p>
            <Badge variant="secondary" className="text-xs">
              {overview?.policies?.active_policies || 0} active
            </Badge>
          </Card>

          {/* ERP/CRM Connectors */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-indigo-500"
            onClick={() => navigate('/connectors')}
          >
            <Database className="w-10 h-10 text-indigo-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Data Connectors</h3>
            <p className="text-sm text-gray-600 mb-3">
              Connect PostgreSQL, MySQL, MongoDB, REST APIs
            </p>
            <Badge variant="secondary" className="text-xs">
              {overview?.connectors?.active_connectors || 0} connected
            </Badge>
          </Card>

          {/* Real-time Alerts */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-red-500"
            onClick={() => navigate('/alerts')}
          >
            <Bell className="w-10 h-10 text-red-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Real-time Alerts</h3>
            <p className="text-sm text-gray-600 mb-3">
              WebSocket, Email, and Slack notifications
            </p>
            <Badge variant="secondary" className="text-xs">
              Active
            </Badge>
          </Card>

          {/* Multi-language Processing */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-teal-500"
            onClick={() => navigate('/upload')}
          >
            <Languages className="w-10 h-10 text-teal-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Multi-language</h3>
            <p className="text-sm text-gray-600 mb-3">
              Process policies in multiple languages
            </p>
            <Badge variant="secondary" className="text-xs">
              Enabled
            </Badge>
          </Card>

          {/* Multi-tenant SaaS */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-cyan-500"
            onClick={() => navigate('/settings')}
          >
            <Cloud className="w-10 h-10 text-cyan-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Multi-tenant</h3>
            <p className="text-sm text-gray-600 mb-3">
              Enterprise SaaS architecture with RBAC
            </p>
            <Badge variant="secondary" className="text-xs">
              Active
            </Badge>
          </Card>

          {/* Production Monitoring */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-yellow-500"
            onClick={() => navigate('/monitoring')}
          >
            <Activity className="w-10 h-10 text-yellow-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Monitoring</h3>
            <p className="text-sm text-gray-600 mb-3">
              Health checks, metrics, and system status
            </p>
            <Badge variant="secondary" className="text-xs">
              {overview?.monitoring?.status || 'Active'}
            </Badge>
          </Card>

          {/* Scalability */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-pink-500"
            onClick={() => navigate('/settings')}
          >
            <TrendingUp className="w-10 h-10 text-pink-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Scalability</h3>
            <p className="text-sm text-gray-600 mb-3">
              Handle millions of records with batch processing
            </p>
            <Badge variant="secondary" className="text-xs">
              Configured
            </Badge>
          </Card>

          {/* Subscription Model */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-emerald-500"
            onClick={() => navigate('/subscription')}
          >
            <Target className="w-10 h-10 text-emerald-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Subscriptions</h3>
            <p className="text-sm text-gray-600 mb-3">
              Manage plan, usage, and billing
            </p>
            <Badge variant="secondary" className="text-xs">
              View Details
            </Badge>
          </Card>

          {/* Auto Installation */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-gray-500"
            onClick={() => window.open('/docs/setup', '_blank')}
          >
            <Settings className="w-10 h-10 text-gray-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Auto Setup</h3>
            <p className="text-sm text-gray-600 mb-3">
              One-command installation and configuration
            </p>
            <Badge variant="secondary" className="text-xs">
              Available
            </Badge>
          </Card>

          {/* Regulatory Mapping */}
          <Card 
            className="p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-violet-500"
            onClick={() => navigate('/upload')}
          >
            <Globe className="w-10 h-10 text-violet-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Regulatory Mapping</h3>
            <p className="text-sm text-gray-600 mb-3">
              Map policies to regulatory frameworks
            </p>
            <Badge variant="secondary" className="text-xs">
              Enabled
            </Badge>
          </Card>
        </div>
      </div>
    </div>
  );
}
