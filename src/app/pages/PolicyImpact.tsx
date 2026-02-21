import { useState, useEffect } from 'react';
import { BarChart3, TrendingDown, Minus, Loader2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { policiesAPI } from '../services/api-enterprise';
import { FeatureLock } from '../components/FeatureLock';

export function PolicyImpact() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const data = await policiesAPI.list(token);
      setPolicies(data);
    } catch (error) {
      console.error('Error loading policies:', error);
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

  const content = (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-green-600" />
            Policy Change Impact Analysis
          </h1>
          <p className="text-gray-600">
            Analyze the impact of policy changes and version updates
          </p>
        </div>

        {/* Info Card */}
        <Card className="p-6 mb-6 bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">How It Works</h3>
          <p className="text-sm text-blue-800">
            When you upload a new version of a policy, the system automatically:
          </p>
          <ul className="list-disc list-inside text-sm text-blue-800 mt-2 space-y-1">
            <li>Compares rules with the previous version</li>
            <li>Identifies modified, new, and removed rules</li>
            <li>Re-scans affected data to calculate impact</li>
            <li>Generates a comprehensive impact report</li>
          </ul>
        </Card>

        {/* Policies List */}
        <div className="space-y-4">
          {policies.length === 0 ? (
            <Card className="p-12 text-center">
              <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Policies Found</h3>
              <p className="text-gray-600 mb-4">
                Upload policies to start tracking impact analysis.
              </p>
              <a
                href="/upload"
                className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Upload Policy
              </a>
            </Card>
          ) : (
            policies.map((policy) => (
              <Card key={policy.policy_id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg mb-1">
                      {policy.policy_name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">Version {policy.version}</Badge>
                      <Badge className={
                        policy.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }>
                        {policy.status}
                      </Badge>
                      {policy.department && (
                        <Badge variant="secondary">{policy.department}</Badge>
                      )}
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    View Impact Report
                  </button>
                </div>

                {policy.regulatory_framework && (
                  <p className="text-sm text-gray-600 mb-2">
                    Framework: {policy.regulatory_framework}
                  </p>
                )}

                <p className="text-sm text-gray-500">
                  Uploaded: {new Date(policy.uploaded_at).toLocaleDateString()}
                </p>
              </Card>
            ))
          )}
        </div>

        {/* Example Impact Report */}
        {policies.length > 0 && (
          <Card className="p-6 mt-6">
            <h3 className="text-lg font-semibold mb-4">Sample Impact Analysis</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="w-5 h-5 text-green-600" />
                  <p className="font-medium text-green-900">Risk Decreased</p>
                </div>
                <p className="text-2xl font-bold text-green-900">-24%</p>
                <p className="text-sm text-green-700">Threshold increased: 10K → 15K</p>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Minus className="w-5 h-5 text-blue-600" />
                  <p className="font-medium text-blue-900">Violations Change</p>
                </div>
                <p className="text-2xl font-bold text-blue-900">42 → 18</p>
                <p className="text-sm text-blue-700">24 violations resolved</p>
              </div>

              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  <p className="font-medium text-purple-900">Rules Modified</p>
                </div>
                <p className="text-2xl font-bold text-purple-900">3</p>
                <p className="text-sm text-purple-700">2 new, 1 removed</p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );

  return (
    <FeatureLock featureName="policy_impact" featureDisplayName="Policy Change Impact Analysis">
      {content}
    </FeatureLock>
  );
}
