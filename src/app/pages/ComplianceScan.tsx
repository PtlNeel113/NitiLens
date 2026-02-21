import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Play, Loader2, AlertTriangle, CheckCircle, FileText, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { extractedRules } from '../data/mockData';
import { api } from '../services/api';

type ScanStatus = 'ready' | 'scanning' | 'complete';

export function ComplianceScan() {
  const navigate = useNavigate();
  const [scanStatus, setScanStatus] = useState<ScanStatus>('ready');
  const [scanProgress, setScanProgress] = useState(0);
  const [violations, setViolations] = useState<any[]>([]);

  const handleStartScan = async () => {
    setScanStatus('scanning');
    setScanProgress(10);

    try {
      // Simulate progress for UI feel
      const progressInterval = setInterval(() => {
        setScanProgress(prev => (prev < 90 ? prev + 2 : prev));
      }, 300);

      // Trigger real backend scan
      await api.triggerScan();

      // Fetch results
      const results = await api.listViolations('open');

      clearInterval(progressInterval);
      setScanProgress(100);

      setTimeout(() => {
        setScanStatus('complete');
        setViolations(results.violations);
      }, 500);
    } catch (error) {
      console.error('Scan failed:', error);
      setScanStatus('ready');
      alert('Compliance scan failed. Please ensure the backend is running at localhost:8000.');
    }
  };

  const severityColors = {
    critical: 'bg-red-100 text-red-700 border-red-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  };

  const getRuleById = (ruleId: string) => {
    return extractedRules.find(r => r.id === ruleId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Compliance Scan</h1>
          <p className="text-gray-600">
            Scan your data against approved policy rules to identify violations
          </p>
        </div>

        {scanStatus === 'ready' && (
          <Card className="p-8">
            <div className="text-center max-w-2xl mx-auto">
              <div className="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                <Play className="w-10 h-10 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold mb-4">Ready to Scan</h2>
              <p className="text-gray-600 mb-6">
                NitiLens will check {extractedRules.length} AML compliance rules against the IBM AML transaction records.
                This process typically takes 30-60 seconds.
              </p>

              <div className="bg-gray-50 rounded-lg p-4 mb-8">
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 mb-1">Records to Scan</p>
                    <p className="text-2xl font-bold text-gray-900">51</p>
                  </div>
                  <div>
                    <p className="text-gray-600 mb-1">AML Rules Active</p>
                    <p className="text-2xl font-bold text-gray-900">{extractedRules.length}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 mb-1">Estimated Time</p>
                    <p className="text-2xl font-bold text-gray-900">~20s</p>
                  </div>
                </div>
              </div>

              <Button onClick={handleStartScan} size="lg" className="text-lg px-8 py-6">
                <Play className="w-5 h-5 mr-2" />
                Run Compliance Scan
              </Button>
            </div>
          </Card>
        )}

        {scanStatus === 'scanning' && (
          <Card className="p-8">
            <div className="text-center max-w-2xl mx-auto">
              <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-6" />
              <h2 className="text-2xl font-bold mb-4">Scanning in Progress...</h2>
              <p className="text-gray-600 mb-6">
                Checking AML rules against IBM transaction records
              </p>

              <div className="space-y-2 mb-6">
                <Progress value={scanProgress} className="h-3" />
                <p className="text-sm text-gray-500">{scanProgress}% complete</p>
              </div>

              <div className="space-y-2 text-sm text-left bg-gray-50 rounded-lg p-4">
                <p className="text-green-600 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Checking large transactions (&gt;$10,000 CTR)...
                </p>
                <p className="text-green-600 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Detecting structuring patterns...
                </p>
                <p className="text-green-600 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Scanning for currency mixing...
                </p>
                <p className="text-blue-600 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Flagging confirmed laundering (Is Laundering = 1)...
                </p>
              </div>
            </div>
          </Card>
        )}

        {scanStatus === 'complete' && (
          <div className="space-y-6">
            <Card className="p-6 bg-yellow-50 border-yellow-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-6 h-6 text-yellow-600" />
                  <div>
                    <h3 className="font-semibold text-yellow-900">Scan Complete</h3>
                    <p className="text-sm text-yellow-700">
                      Found {violations.length} compliance violations requiring review
                    </p>
                  </div>
                </div>
                <Button onClick={() => navigate('/review')}>
                  Review Queue
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Violation Summary</h2>

              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-3xl font-bold text-red-600">
                    {violations.filter(v => v.severity === 'critical').length}
                  </p>
                  <p className="text-sm text-red-700">Critical</p>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-3xl font-bold text-orange-600">
                    {violations.filter(v => v.severity === 'high').length}
                  </p>
                  <p className="text-sm text-orange-700">High</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-3xl font-bold text-yellow-600">
                    {violations.filter(v => v.severity === 'medium').length}
                  </p>
                  <p className="text-sm text-yellow-700">Medium</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">
                    {violations.filter(v => v.severity === 'low').length}
                  </p>
                  <p className="text-sm text-green-700">Low</p>
                </div>
              </div>

              <h3 className="font-semibold mb-4">Detected Violations</h3>
              <div className="space-y-3">
                {violations.map((violation) => {
                  const rule = extractedRules.find(r => r.id === violation.rule_id);
                  return (
                    <Card key={violation.id} className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge className={(severityColors as any)[violation.severity]}>
                              {violation.severity.toUpperCase()}
                            </Badge>
                            <span className="text-sm text-gray-600">TXN: {violation.transaction_id}</span>
                          </div>
                          <h4 className="font-semibold text-gray-900 mb-1">{violation.rule_name}</h4>
                        </div>
                      </div>

                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                        <p className="text-sm text-gray-900">{violation.explanation}</p>
                      </div>

                      <div className="bg-gray-50 rounded p-3 mb-2">
                        <p className="text-xs font-medium text-gray-700 mb-2">Evidence:</p>
                        <div className="grid md:grid-cols-2 gap-2 text-xs">
                          {Object.entries(violation.evidence).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-gray-600">{key}:</span>{' '}
                              <span className="font-mono text-gray-900">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {rule && (
                        <p className="text-xs text-gray-500">
                          <FileText className="w-3 h-3 inline mr-1" />
                          Source: {rule.sourceReference}
                        </p>
                      )}
                    </Card>
                  );
                })}
              </div>

              <div className="mt-6 flex justify-end pt-6 border-t">
                <Button onClick={() => navigate('/review')} size="lg">
                  Go to Review Queue
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
