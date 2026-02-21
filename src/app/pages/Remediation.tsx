import { useState, useEffect } from 'react';
import { Shield, Clock, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { remediationAPI } from '../services/api-enterprise';
import { FeatureLock } from '../components/FeatureLock';

export function Remediation() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadCases();
  }, [filter]);

  const loadCases = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const filters = filter !== 'all' ? { status: filter } : {};
      const data = await remediationAPI.getCases(token, filters);
      setCases(data);
    } catch (error) {
      console.error('Error loading cases:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'overdue': return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'in_progress': return <Clock className="w-5 h-5 text-blue-600" />;
      default: return <Shield className="w-5 h-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  const content = (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Shield className="w-8 h-8 text-blue-600" />
            Automated Remediation Engine
          </h1>
          <p className="text-gray-600">
            Manage violation lifecycle from detection to resolution
          </p>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          {['all', 'open', 'in_progress', 'overdue', 'completed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {status.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>

        {/* Cases List */}
        <div className="space-y-4">
          {cases.length === 0 ? (
            <Card className="p-12 text-center">
              <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Cases Found</h3>
              <p className="text-gray-600">
                No remediation cases match your current filter.
              </p>
            </Card>
          ) : (
            cases.map((case_) => (
              <Card key={case_.case_id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(case_.status)}
                      <h3 className="font-semibold text-gray-900">
                        Case #{case_.case_id.slice(0, 8)}
                      </h3>
                      <Badge className={getPriorityColor(case_.priority)}>
                        {case_.priority}
                      </Badge>
                      <Badge variant="outline">{case_.status.replace('_', ' ')}</Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">
                      {case_.recommended_action}
                    </p>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>Assigned to: {case_.assigned_to_name || 'Unassigned'}</span>
                      <span>Due: {new Date(case_.due_date).toLocaleDateString()}</span>
                      <span>Created: {new Date(case_.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    View Details
                  </button>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );

  return (
    <FeatureLock featureName="remediation" featureDisplayName="Automated Remediation Engine">
      {content}
    </FeatureLock>
  );
}
