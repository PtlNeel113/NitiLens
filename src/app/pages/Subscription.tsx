import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { subscriptionAPI } from '../services/api-enterprise';
import { CheckCircle2, XCircle, AlertTriangle, TrendingUp, Users, FileText, Activity } from 'lucide-react';

interface PlanFeatures {
  anomaly_detection: boolean;
  remediation: boolean;
  regulatory_mapping: boolean;
  monitoring: boolean;
  policy_impact: boolean;
  multi_language: boolean;
}

interface Plan {
  name: string;
  max_policies: number | string;
  max_transactions_per_month: number | string;
  max_users: number | string;
  price_monthly: number;
  features: PlanFeatures;
}

interface UsageData {
  plan: { name: string; price_monthly: number };
  subscription: {
    status: string;
    started_at: string;
    expires_at: string;
    auto_renew: boolean;
  };
  limits: {
    policies: { current: number; limit: number | string; percentage: number };
    transactions: { current: number; limit: number | string; percentage: number };
    users: { current: number; limit: number | string; percentage: number };
  };
  features: PlanFeatures;
}

const Subscription: React.FC = () => {
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [upgrading, setUpgrading] = useState(false);

  const token = localStorage.getItem('token') || '';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usageData, plansData] = await Promise.all([
        subscriptionAPI.getUsage(token),
        subscriptionAPI.listPlans(token),
      ]);
      setUsage(usageData);
      setPlans(plansData);
    } catch (err: any) {
      setError(err.message || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planName: string) => {
    if (!confirm(`Upgrade to ${planName} plan?`)) return;
    
    try {
      setUpgrading(true);
      await subscriptionAPI.upgrade(token, planName);
      await loadData();
      alert('Plan upgraded successfully!');
    } catch (err: any) {
      alert(err.message || 'Failed to upgrade plan');
    } finally {
      setUpgrading(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Cancel subscription? It will remain active until the end of the billing period.')) return;
    
    try {
      await subscriptionAPI.cancel(token);
      await loadData();
      alert('Subscription cancelled. Auto-renewal disabled.');
    } catch (err: any) {
      alert(err.message || 'Failed to cancel subscription');
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !usage) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertDescription>{error || 'No subscription data available'}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Subscription Management</h1>
        <p className="text-gray-600 mt-2">Manage your plan, usage, and billing</p>
      </div>

      {/* Current Plan */}
      <Card>
        <CardHeader>
          <CardTitle>Current Plan</CardTitle>
          <CardDescription>Your active subscription details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold">{usage.plan.name}</h3>
              <p className="text-gray-600">${usage.plan.price_monthly}/month</p>
              <div className="mt-2 flex items-center gap-2">
                <Badge variant={usage.subscription.status === 'active' ? 'default' : 'secondary'}>
                  {usage.subscription.status}
                </Badge>
                {usage.subscription.auto_renew ? (
                  <Badge variant="outline">Auto-renew enabled</Badge>
                ) : (
                  <Badge variant="destructive">Auto-renew disabled</Badge>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Expires: {new Date(usage.subscription.expires_at).toLocaleDateString()}
              </p>
            </div>
            {usage.subscription.auto_renew && (
              <Button variant="outline" onClick={handleCancel}>
                Cancel Subscription
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Usage Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Usage This Month</CardTitle>
          <CardDescription>Track your resource consumption</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Policies */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Policies</span>
              </div>
              <span className={`font-bold ${getUsageColor(usage.limits.policies.percentage)}`}>
                {usage.limits.policies.current} / {usage.limits.policies.limit}
              </span>
            </div>
            {typeof usage.limits.policies.limit === 'number' && (
              <Progress 
                value={usage.limits.policies.percentage} 
                className={getProgressColor(usage.limits.policies.percentage)}
              />
            )}
          </div>

          {/* Transactions */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                <span className="font-medium">Transactions Scanned</span>
              </div>
              <span className={`font-bold ${getUsageColor(usage.limits.transactions.percentage)}`}>
                {usage.limits.transactions.current.toLocaleString()} / {
                  typeof usage.limits.transactions.limit === 'number' 
                    ? usage.limits.transactions.limit.toLocaleString() 
                    : usage.limits.transactions.limit
                }
              </span>
            </div>
            {typeof usage.limits.transactions.limit === 'number' && (
              <Progress 
                value={usage.limits.transactions.percentage} 
                className={getProgressColor(usage.limits.transactions.percentage)}
              />
            )}
          </div>

          {/* Users */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-green-600" />
                <span className="font-medium">Active Users</span>
              </div>
              <span className={`font-bold ${getUsageColor(usage.limits.users.percentage)}`}>
                {usage.limits.users.current} / {usage.limits.users.limit}
              </span>
            </div>
            {typeof usage.limits.users.limit === 'number' && (
              <Progress 
                value={usage.limits.users.percentage} 
                className={getProgressColor(usage.limits.users.percentage)}
              />
            )}
          </div>

          {/* Warning if approaching limits */}
          {(usage.limits.policies.percentage >= 80 || 
            usage.limits.transactions.percentage >= 80 || 
            usage.limits.users.percentage >= 80) && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                You're approaching your plan limits. Consider upgrading to avoid service interruption.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Available Plans */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <Card 
              key={plan.name} 
              className={plan.name === usage.plan.name ? 'border-blue-500 border-2' : ''}
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {plan.name}
                  {plan.name === usage.plan.name && (
                    <Badge>Current</Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  <span className="text-3xl font-bold text-gray-900">${plan.price_monthly}</span>
                  <span className="text-gray-600">/month</span>
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    <span>{plan.max_policies} policies</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    <span>
                      {typeof plan.max_transactions_per_month === 'number'
                        ? `${(plan.max_transactions_per_month / 1000).toLocaleString()}K`
                        : plan.max_transactions_per_month} transactions/month
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    <span>{plan.max_users} users</span>
                  </div>
                </div>

                <div className="border-t pt-4 space-y-2">
                  <p className="font-medium text-sm">Features:</p>
                  <div className="space-y-1 text-sm">
                    {Object.entries(plan.features).map(([key, enabled]) => (
                      <div key={key} className="flex items-center gap-2">
                        {enabled ? (
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                        ) : (
                          <XCircle className="w-4 h-4 text-gray-300" />
                        )}
                        <span className={enabled ? '' : 'text-gray-400'}>
                          {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {plan.name !== usage.plan.name && (
                  <Button 
                    className="w-full" 
                    onClick={() => handleUpgrade(plan.name)}
                    disabled={upgrading}
                  >
                    <TrendingUp className="w-4 h-4 mr-2" />
                    {upgrading ? 'Upgrading...' : 'Upgrade'}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Subscription;
