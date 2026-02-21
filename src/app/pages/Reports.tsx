import { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Shield, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { extractedRules } from '../data/mockData';
import { api, type ComplianceSummary } from '../services/api';

export function Reports() {
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [violations, setViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [sum, results] = await Promise.all([
          api.getComplianceSummary(),
          api.listViolations()
        ]);
        setSummary(sum);
        setViolations(results.violations);
      } catch (error) {
        console.error('Failed to load report data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleGenerateReport = () => {
    alert('Report generated successfully! In a production environment, this would download a PDF.');
  };

  const handleExportCSV = () => {
    alert('Data exported successfully! In a production environment, this would download a CSV file.');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  const reportDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });


  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Compliance Reports</h1>
          <p className="text-gray-600">
            Generate audit-ready compliance reports with full transparency
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <FileText className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Full Compliance Report</h3>
            <p className="text-sm text-gray-600 mb-4">
              Complete report with all violations, evidence, and reviewer decisions
            </p>
            <Button onClick={handleGenerateReport} className="w-full">
              <Download className="w-4 h-4 mr-2" />
              Generate PDF
            </Button>
          </Card>

          <Card className="p-6">
            <FileText className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Executive Summary</h3>
            <p className="text-sm text-gray-600 mb-4">
              High-level overview for leadership and stakeholders
            </p>
            <Button onClick={handleGenerateReport} className="w-full" variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Generate PDF
            </Button>
          </Card>

          <Card className="p-6">
            <FileText className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Export Data</h3>
            <p className="text-sm text-gray-600 mb-4">
              Raw data export for further analysis or integration
            </p>
            <Button onClick={handleExportCSV} className="w-full" variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </Card>
        </div>

        {/* Report Preview */}
        <Card className="p-8">
          <div className="border-b pb-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-1">Compliance Report Preview</h2>
                <p className="text-sm text-gray-600">Generated on {reportDate}</p>
              </div>
              <Badge className="bg-green-100 text-green-700 border-green-300">
                <Shield className="w-4 h-4 mr-1" />
                AUDIT READY
              </Badge>
            </div>
          </div>

          {/* Executive Summary Section */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4">Executive Summary</h3>
            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Active Rules</p>
                <p className="text-3xl font-bold text-blue-600">6</p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Open Violations</p>
                <p className="text-3xl font-bold text-red-600">{summary?.open_violations ?? 0}</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Resolved</p>
                <p className="text-3xl font-bold text-green-600">{summary?.resolved_violations ?? 0}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">False Positives</p>
                <p className="text-3xl font-bold text-gray-600">{summary?.false_positives ?? 0}</p>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-900">
                <strong>Risk Assessment:</strong> {summary?.severity_breakdown.critical ?? 0} critical and {summary?.severity_breakdown.high ?? 0} high-severity
                AML violations require immediate attention. CTR filings and SAR submissions are pending for open violations.
              </p>
            </div>
          </div>

          {/* Policy Rules Section */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4">Enforced Policy Rules</h3>
            <div className="space-y-3">
              {extractedRules.map((rule) => (
                <div key={rule.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">{rule.description}</h4>
                    <Badge className={
                      rule.severity === 'critical' ? 'bg-red-100 text-red-700' :
                        rule.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                          rule.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                    }>
                      {rule.severity.toUpperCase()}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">Category: {rule.category}</p>
                  <p className="text-xs text-gray-500">Source: {rule.sourceReference}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Violations Detail Section */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4">Violation Details</h3>
            <div className="space-y-4">
              {violations.map((violation) => (
                <div key={violation.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={
                          violation.severity === 'critical' ? 'bg-red-100 text-red-700' :
                            violation.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                              violation.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-green-100 text-green-700'
                        }>
                          {violation.severity.toUpperCase()}
                        </Badge>
                        <Badge className={
                          violation.status === 'resolved' ? 'bg-green-100 text-green-700' :
                            violation.status === 'open' ? 'bg-red-100 text-red-700' :
                              'bg-gray-100 text-gray-700'
                        }>
                          {violation.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                      <h4 className="font-semibold text-gray-900 mb-1">
                        {violation.rule_name}
                      </h4>
                    </div>
                    <span className="text-sm text-gray-600 font-mono">TXN: {violation.transaction_id}</span>
                  </div>

                  <div className="bg-gray-50 rounded p-3 mb-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Explanation:</p>
                    <p className="text-sm text-gray-900">{violation.explanation}</p>
                  </div>

                  <div className="bg-gray-50 rounded p-3 mb-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Evidence:</p>
                    <div className="grid md:grid-cols-2 gap-2 text-sm">
                      {Object.entries(violation.evidence).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-gray-600">{key}:</span>{' '}
                          <span className="font-mono text-gray-900">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {violation.reviewer_notes && (
                    <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-3">
                      <p className="text-sm font-medium text-blue-900 mb-1">Reviewer Decision:</p>
                      <p className="text-sm text-blue-800">{violation.reviewer_notes}</p>
                    </div>
                  )}

                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>
                      <Calendar className="w-3 h-3 inline mr-1" />
                      Detected: {new Date(violation.detected_at).toLocaleString()}
                    </span>
                    {violation.reviewed_at && (
                      <span>
                        <CheckCircle className="w-3 h-3 inline mr-1" />
                        Reviewed: {new Date(violation.reviewed_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Audit Trail Section */}
          <div className="border-t pt-6">
            <h3 className="text-xl font-semibold mb-4">Audit Trail Information</h3>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-green-900 mb-2">This report is audit-ready and includes:</p>
                  <ul className="text-sm text-green-800 space-y-1">
                    <li>✓ Complete policy references with source citations</li>
                    <li>✓ Full evidence trail for each violation</li>
                    <li>✓ Human reviewer decisions and comments</li>
                    <li>✓ Timestamps for all actions</li>
                    <li>✓ Severity classifications and risk assessments</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 pt-6 border-t flex gap-4">
            <Button onClick={handleGenerateReport} size="lg">
              <Download className="w-4 h-4 mr-2" />
              Download Full Report (PDF)
            </Button>
            <Button onClick={handleExportCSV} size="lg" variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export Data (CSV)
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
