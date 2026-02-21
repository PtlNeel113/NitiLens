import { useState, useEffect } from 'react';
import { TrendingUp, AlertTriangle, Activity, Loader2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { riskAPI } from '../services/api-enterprise';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { FeatureLock } from '../components/FeatureLock';

export function Risk() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRiskDashboard();
  }, []);

  const loadRiskDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const data = await riskAPI.getDashboard(token);
      setDashboard(data);
    } catch (error) {
      console.error('Error loading risk dashboard:', error);
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
            <TrendingUp className="w-8 h-8 text-orange-600" />
            Risk Intelligence & Anomaly Detection
          </h1>
          <p className="text-gray-600">
            ML-powered predictive risk analysis and anomaly detection
          </p>
        </div>

        {/* Risk Trend */}
        {dashboard?.current_trend && (
          <Card className="p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Risk Trend</h3>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Current Week Avg</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard.current_trend.current_week_avg?.toFixed(2) || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Previous Week Avg</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard.current_trend.previous_week_avg?.toFixed(2) || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Change</p>
                <p className={`text-2xl font-bold ${
                  dashboard.current_trend.change_percent > 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {dashboard.current_trend.change_percent > 0 ? '+' : ''}
                  {dashboard.current_trend.change_percent?.toFixed(1) || '0'}%
                </p>
              </div>
            </div>
            {dashboard.current_trend.alert && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <p className="text-sm font-medium text-red-900">
                    {dashboard.current_trend.alert}
                  </p>
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Top Anomalies */}
        <Card className="p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Top Anomalies Detected</h3>
          {dashboard?.top_anomalies && dashboard.top_anomalies.length > 0 ? (
            <div className="space-y-3">
              {dashboard.top_anomalies.map((anomaly: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      Transaction #{anomaly.transaction_id?.slice(0, 8)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Amount: ${anomaly.amount?.toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge className={
                      anomaly.anomaly_score > 0.9 ? 'bg-red-100 text-red-800' :
                      anomaly.anomaly_score > 0.8 ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }>
                      Score: {(anomaly.anomaly_score * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No anomalies detected</p>
            </div>
          )}
        </Card>

        {/* Risk Heatmap */}
        {dashboard?.risk_heatmap && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Risk Heatmap</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboard.risk_heatmap}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="risk_level" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#f97316" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        )}
      </div>
    </div>
  );

  return (
    <FeatureLock featureName="anomaly_detection" featureDisplayName="Risk Intelligence & Anomaly Detection">
      {content}
    </FeatureLock>
  );
}
