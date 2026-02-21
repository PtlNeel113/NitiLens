import React, { useEffect, useState } from 'react';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Lock, TrendingUp } from 'lucide-react';
import { subscriptionAPI } from '../services/api-enterprise';
import { useNavigate } from 'react-router';

interface FeatureLockProps {
  featureName: string;
  featureDisplayName: string;
  children: React.ReactNode;
}

export const FeatureLock: React.FC<FeatureLockProps> = ({ 
  featureName, 
  featureDisplayName, 
  children 
}) => {
  const [isEnabled, setIsEnabled] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPlan, setCurrentPlan] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    checkFeatureAccess();
  }, [featureName]);

  const checkFeatureAccess = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setIsEnabled(false);
        setLoading(false);
        return;
      }

      const usage = await subscriptionAPI.getUsage(token);
      const enabled = usage.features[featureName] || false;
      setIsEnabled(enabled);
      setCurrentPlan(usage.plan.name);
    } catch (error) {
      console.error('Error checking feature access:', error);
      setIsEnabled(false);
    } finally {
      setLoading(false);
    }
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

  if (isEnabled === false) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              {featureDisplayName}
              <Badge variant="destructive" className="ml-2">
                <Lock className="w-3 h-3 mr-1" />
                Locked
              </Badge>
            </h1>
            <p className="text-gray-600 mt-2">This feature is not available in your current plan</p>
          </div>
        </div>

        <Alert className="border-yellow-500 bg-yellow-50">
          <Lock className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            <div className="space-y-3">
              <p className="font-medium">
                {featureDisplayName} is not available in the {currentPlan} plan.
              </p>
              <p>
                Upgrade to Pro or Enterprise to unlock this feature and gain access to:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Advanced analytics and insights</li>
                <li>Automated workflows</li>
                <li>Priority support</li>
                <li>Higher usage limits</li>
              </ul>
              <div className="pt-2">
                <Button 
                  onClick={() => navigate('/subscription')}
                  className="bg-yellow-600 hover:bg-yellow-700"
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Upgrade Plan
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>

        {/* Show blurred preview */}
        <div className="relative">
          <div className="blur-sm pointer-events-none opacity-50">
            {children}
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-white/90 p-6 rounded-lg shadow-lg text-center">
              <Lock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-lg font-semibold text-gray-700">Feature Locked</p>
              <p className="text-sm text-gray-600 mt-1">Upgrade to access</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
