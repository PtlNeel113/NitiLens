import { useState, useEffect } from 'react';
import { CheckCircle, X, MessageSquare, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { extractedRules, type Violation } from '../data/mockData';
import { api } from '../services/api';

export function ReviewQueue() {
  const [violations, setViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedViolation, setSelectedViolation] = useState<any | null>(null);
  const [comment, setComment] = useState('');

  const loadViolations = async () => {
    try {
      setLoading(true);
      const data = await api.listViolations();
      setViolations(data.violations);
    } catch (error) {
      console.error('Failed to load violations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadViolations();
  }, []);

  const handleReview = async (violationId: string, action: 'resolve' | 'dismiss', reviewComment: string) => {
    try {
      await api.submitReviewAction(violationId, action, reviewComment);
      await loadViolations();
      setSelectedViolation(null);
      setComment('');
    } catch (error) {
      console.error('Action failed:', error);
      alert('Failed to submit review action.');
    }
  };

  const severityColors = {
    critical: 'bg-red-100 text-red-700 border-red-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  };

  const statusColors = {
    open: 'bg-red-100 text-red-700',
    reviewed: 'bg-blue-100 text-blue-700',
    resolved: 'bg-green-100 text-green-700',
    false_positive: 'bg-gray-100 text-gray-700'
  };

  const getRuleById = (ruleId: string) => {
    return extractedRules.find(r => r.id === ruleId);
  };

  const openViolations = violations.filter(v => v.status === 'open');
  const reviewedViolations = violations.filter(v => v.status === 'reviewed');
  const resolvedViolations = violations.filter(v => v.status === 'resolved');
  const falsePositives = violations.filter(v => v.status === 'false_positive');

  const ViolationList = ({ items, showActions = true }: { items: any[], showActions?: boolean }) => (
    <div className="space-y-3">
      {items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
          <p>No violations in this category</p>
        </div>
      ) : (
        items.map((violation) => {
          return (
            <Card key={violation.id} className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={(severityColors as any)[violation.severity]}>
                      {violation.severity.toUpperCase()}
                    </Badge>
                    <Badge className={(statusColors as any)[violation.status]}>
                      {violation.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">{violation.rule_name}</h4>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                <p className="text-sm text-gray-600 mb-1 font-mono text-xs">TXN: {violation.transaction_id}</p>
                <p className="text-sm text-gray-900">{violation.explanation}</p>
              </div>

              <div className="bg-gray-50 rounded p-3 mb-3">
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

              {violation.reviewer_notes && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                  <div className="flex items-start gap-2">
                    <MessageSquare className="w-4 h-4 text-blue-600 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-xs font-medium text-blue-900 mb-1">Reviewer Comment:</p>
                      <p className="text-sm text-blue-800">{violation.reviewer_notes}</p>
                    </div>
                  </div>
                </div>
              )}

              {showActions && violation.status === 'open' && (
                <div className="flex gap-2 mt-3">
                  <Button
                    size="sm"
                    onClick={() => setSelectedViolation(violation)}
                    variant="outline"
                  >
                    Review
                  </Button>
                </div>
              )}
            </Card>
          );
        })
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Review Queue</h1>
          <p className="text-gray-600">
            Review and take action on compliance violations
          </p>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-900">
              <strong>Remember:</strong> Humans decide. Review each violation carefully
              and add context for audit trails.
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4 text-center">
            <p className="text-3xl font-bold text-red-600">{openViolations.length}</p>
            <p className="text-sm text-gray-600">Open</p>
          </Card>
          <Card className="p-4 text-center">
            <p className="text-3xl font-bold text-blue-600">{reviewedViolations.length}</p>
            <p className="text-sm text-gray-600">Reviewed</p>
          </Card>
          <Card className="p-4 text-center">
            <p className="text-3xl font-bold text-green-600">{resolvedViolations.length}</p>
            <p className="text-sm text-gray-600">Resolved</p>
          </Card>
          <Card className="p-4 text-center">
            <p className="text-3xl font-bold text-gray-600">{falsePositives.length}</p>
            <p className="text-sm text-gray-600">False Positives</p>
          </Card>
        </div>

        <Card className="p-6">
          <Tabs defaultValue="open">
            <TabsList>
              <TabsTrigger value="open">Open ({openViolations.length})</TabsTrigger>
              <TabsTrigger value="reviewed">Reviewed ({reviewedViolations.length})</TabsTrigger>
              <TabsTrigger value="resolved">Resolved ({resolvedViolations.length})</TabsTrigger>
              <TabsTrigger value="false">False Positives ({falsePositives.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="open" className="mt-4">
              <ViolationList items={openViolations} />
            </TabsContent>

            <TabsContent value="reviewed" className="mt-4">
              <ViolationList items={reviewedViolations} showActions={false} />
            </TabsContent>

            <TabsContent value="resolved" className="mt-4">
              <ViolationList items={resolvedViolations} showActions={false} />
            </TabsContent>

            <TabsContent value="false" className="mt-4">
              <ViolationList items={falsePositives} showActions={false} />
            </TabsContent>
          </Tabs>
        </Card>
      </div>

      {/* Review Modal */}
      {selectedViolation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-2xl w-full p-6">
            <h3 className="text-xl font-bold mb-4">Review Violation</h3>

            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Badge className={(severityColors as any)[selectedViolation.severity]}>
                  {selectedViolation.severity.toUpperCase()}
                </Badge>
                <span className="text-sm text-gray-600">TXN: {selectedViolation.transaction_id}</span>
              </div>
              <p className="font-semibold mb-2">{selectedViolation.rule_name}</p>
              <p className="text-sm text-gray-700 bg-yellow-50 p-3 rounded">
                {selectedViolation.explanation}
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Add Comment (Optional)</label>
              <Textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Add context for the audit trail..."
                rows={3}
              />
            </div>

            <div className="flex gap-3">
              <Button
                onClick={() => handleReview(selectedViolation.id, 'resolve', comment || 'Confirmed violation.')}
                className="flex-1"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Confirm Violation
              </Button>
              <Button
                onClick={() => handleReview(selectedViolation.id, 'dismiss', comment || 'Marked as false positive.')}
                variant="outline"
                className="flex-1"
              >
                <X className="w-4 h-4 mr-2" />
                False Positive
              </Button>
              <Button
                onClick={() => {
                  setSelectedViolation(null);
                  setComment('');
                }}
                variant="ghost"
              >
                Cancel
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
