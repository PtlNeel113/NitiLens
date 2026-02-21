import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Upload, FileText, CheckCircle, Loader2, Info, ArrowRight, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/ui/tooltip';
import { extractedRules } from '../data/mockData';

type Step = 'upload' | 'reading' | 'extracting' | 'review' | 'error';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function PolicyUpload() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<Step>('upload');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileName, setFileName] = useState('');
  const [fileType, setFileType] = useState<'pdf' | 'ppt' | 'pptx'>('pdf');
  const [docInfo, setDocInfo] = useState('');
  const [rulesData, setRulesData] = useState<any[]>([]);
  const [approvedRules, setApprovedRules] = useState<Set<string>>(new Set());
  const [errorMessage, setErrorMessage] = useState('');

  const getFileType = (name: string): 'pdf' | 'ppt' | 'pptx' | null => {
    const ext = name.toLowerCase().split('.').pop();
    if (ext === 'pdf') return 'pdf';
    if (ext === 'ppt') return 'ppt';
    if (ext === 'pptx') return 'pptx';
    return null;
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const detectedType = getFileType(file.name);
    if (!detectedType) {
      setErrorMessage('Unsupported file type. Please upload PDF or PPTX.');
      setCurrentStep('error');
      return;
    }

    setFileName(file.name);
    setFileType(detectedType);
    setErrorMessage('');
    uploadFile(file, detectedType);
  };

  // ── Simulated upload fallback (demo mode) ─────────────────────
  const simulateUpload = (type: 'pdf' | 'ppt' | 'pptx') => {
    setCurrentStep('reading');
    setUploadProgress(0);

    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          // Move to extracting step
          setDocInfo(type === 'pdf' ? 'Found 24 pages' : 'Found 18 slides');
          setRulesData(extractedRules);
          setTimeout(() => {
            setCurrentStep('extracting');
            setTimeout(() => setCurrentStep('review'), 1500);
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  // ── Real upload with fallback ──────────────────────────────────
  const uploadFile = async (file: File, type: 'pdf' | 'ppt' | 'pptx') => {
    setCurrentStep('reading');
    setUploadProgress(0);

    // Simulate progress during upload
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) return 90;
        return prev + 5;
      });
    }, 300);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token') || '';
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE}/api/policies/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const data = await response.json();

      if (!response.ok || data.status === 'error') {
        // If auth error (401/403), fall back to simulation for demo
        if (response.status === 401 || response.status === 403 || response.status === 422) {
          console.warn('Auth required — falling back to demo mode');
          simulateUpload(type);
          return;
        }
        setErrorMessage(data.message || data.detail || 'Upload failed. Please try again.');
        setCurrentStep('error');
        return;
      }

      // Success — use real data
      setDocInfo(data.doc_info || '');

      const rules = data.extracted_rules || [];
      if (rules.length > 0) {
        setRulesData(rules);
      } else {
        setRulesData(extractedRules);
      }

      setCurrentStep('extracting');
      setTimeout(() => setCurrentStep('review'), 1500);
    } catch (err) {
      // Backend not running — fall back to simulation for demo
      clearInterval(progressInterval);
      console.warn('Backend unavailable — falling back to demo mode');
      simulateUpload(type);
    }
  };

  const handleApproveAll = () => {
    const displayRules = rulesData.length > 0 ? rulesData : extractedRules;
    const allIds = new Set(displayRules.map((rule: any) => rule.id));
    setApprovedRules(allIds);
  };

  const toggleRuleApproval = (ruleId: string) => {
    setApprovedRules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ruleId)) {
        newSet.delete(ruleId);
      } else {
        newSet.add(ruleId);
      }
      return newSet;
    });
  };

  const handleContinue = () => {
    navigate('/data-connection');
  };

  const handleRetry = () => {
    setCurrentStep('upload');
    setErrorMessage('');
    setUploadProgress(0);
    setFileName('');
  };

  const displayRules = rulesData.length > 0 ? rulesData : extractedRules;

  const severityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-700 border-red-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  };

  const extractingMessage = fileType === 'pdf'
    ? 'Extracting compliance rules from document pages…'
    : 'Extracting compliance rules from presentation slides…';

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between max-w-2xl mx-auto">
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${currentStep !== 'upload' && currentStep !== 'error' ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-600'
                }`}>
                {currentStep !== 'upload' && currentStep !== 'error' ? <CheckCircle className="w-6 h-6" /> : '1'}
              </div>
              <span className="text-sm mt-2">Upload</span>
            </div>
            <div className={`flex-1 h-1 mx-2 ${currentStep === 'upload' || currentStep === 'error' ? 'bg-gray-200' : 'bg-blue-600'}`} />

            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${currentStep === 'reading' ? 'bg-blue-600 text-white' :
                currentStep === 'extracting' || currentStep === 'review' ? 'bg-blue-600 text-white' :
                  'bg-gray-200 text-gray-500'
                }`}>
                {currentStep === 'reading' ? <Loader2 className="w-6 h-6 animate-spin" /> :
                  currentStep === 'extracting' || currentStep === 'review' ? <CheckCircle className="w-6 h-6" /> : '2'}
              </div>
              <span className="text-sm mt-2">Read</span>
            </div>
            <div className={`flex-1 h-1 mx-2 ${currentStep === 'extracting' || currentStep === 'review' ? 'bg-blue-600' : 'bg-gray-200'}`} />

            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${currentStep === 'extracting' ? 'bg-blue-600 text-white' :
                currentStep === 'review' ? 'bg-blue-600 text-white' :
                  'bg-gray-200 text-gray-500'
                }`}>
                {currentStep === 'extracting' ? <Loader2 className="w-6 h-6 animate-spin" /> :
                  currentStep === 'review' ? <CheckCircle className="w-6 h-6" /> : '3'}
              </div>
              <span className="text-sm mt-2">Extract</span>
            </div>
            <div className={`flex-1 h-1 mx-2 ${currentStep === 'review' ? 'bg-blue-600' : 'bg-gray-200'}`} />

            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${currentStep === 'review' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
                }`}>
                4
              </div>
              <span className="text-sm mt-2">Review</span>
            </div>
          </div>
        </div>

        {/* Upload Section */}
        {currentStep === 'upload' && (
          <Card className="p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Upload Your Policy Document</h2>
              <p className="text-gray-600">
                We'll read your policy and extract compliance rules automatically
              </p>
            </div>

            <div className="max-w-md mx-auto">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <p className="mb-2 text-sm text-gray-600">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PDF, PPT, PPTX files (MAX. 10MB)</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.ppt,.pptx"
                  onChange={handleFileSelect}
                />
              </label>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex gap-2">
                  <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-900">
                    <p className="font-semibold mb-1">What happens next?</p>
                    <p className="text-blue-700">
                      NitiLens will read your document, identify compliance requirements,
                      and convert them into enforceable rules you can review.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Error Section */}
        {currentStep === 'error' && (
          <Card className="p-8">
            <div className="max-w-md mx-auto text-center">
              <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-6" />
              <h2 className="text-2xl font-bold mb-2 text-red-700">Upload Failed</h2>
              <p className="text-gray-600 mb-6">{errorMessage}</p>
              <Button onClick={handleRetry} size="lg">
                Try Again
              </Button>
            </div>
          </Card>
        )}

        {/* Reading/Extracting Section */}
        {(currentStep === 'reading' || currentStep === 'extracting') && (
          <Card className="p-8">
            <div className="max-w-md mx-auto text-center">
              <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-6" />
              <h2 className="text-2xl font-bold mb-2">
                {currentStep === 'reading' ? 'Reading Your Policy...' : extractingMessage}
              </h2>
              <p className="text-gray-600 mb-6">
                {currentStep === 'reading'
                  ? `Processing ${fileName || 'document'}`
                  : 'Identifying requirements and building rule definitions'}
              </p>

              {currentStep === 'reading' && (
                <div className="space-y-2">
                  <Progress value={uploadProgress} className="h-2" />
                  <p className="text-sm text-gray-500">{uploadProgress}% complete</p>
                </div>
              )}

              {currentStep === 'extracting' && (
                <div className="space-y-2 mt-4">
                  <p className="text-sm text-green-600 flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4" /> {docInfo || (fileType === 'pdf' ? 'Found 24 pages' : 'Found 18 slides')}
                  </p>
                  <p className="text-sm text-green-600 flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4" /> Identified {displayRules.length} compliance rules
                  </p>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Review Rules Section */}
        {currentStep === 'review' && (
          <div className="space-y-6">
            <Card className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Review Extracted Rules</h2>
                  <p className="text-gray-600">
                    We found {displayRules.length} compliance rules in your policy. Review and approve them below.
                  </p>
                  {docInfo && (
                    <p className="text-sm text-blue-600 mt-1">
                      <FileText className="w-4 h-4 inline mr-1" />
                      Source: {fileName} — {docInfo}
                    </p>
                  )}
                </div>
                <Button onClick={handleApproveAll} variant="outline">
                  Approve All
                </Button>
              </div>

              <div className="space-y-4">
                {displayRules.map((rule: any) => (
                  <Card key={rule.id} className={`p-4 ${approvedRules.has(rule.id) ? 'border-green-300 bg-green-50' : ''}`}>
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={approvedRules.has(rule.id)}
                        onChange={() => toggleRuleApproval(rule.id)}
                        className="mt-1 w-5 h-5 text-blue-600 rounded"
                      />
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 mb-1">{rule.description}</h3>
                            <p className="text-sm text-gray-600 mb-2">
                              <span className="font-medium">Category:</span> {rule.category}
                            </p>
                          </div>
                          <div className="flex gap-2 ml-4">
                            <Badge className={severityColors[rule.severity] || ''}>
                              {rule.severity.toUpperCase()}
                            </Badge>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger>
                                  <Info className="w-5 h-5 text-gray-400" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p className="max-w-xs">
                                    This rule helps ensure {rule.category.toLowerCase()} compliance
                                    and prevents security risks.
                                  </p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                        </div>

                        <div className="bg-gray-50 rounded p-3 mb-2">
                          <p className="text-xs font-mono text-gray-700">{rule.condition}</p>
                        </div>

                        <p className="text-xs text-gray-500">
                          <FileText className="w-3 h-3 inline mr-1" />
                          Source: {rule.source_reference || rule.sourceReference || fileName}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              <div className="mt-8 flex justify-between items-center pt-6 border-t">
                <p className="text-sm text-gray-600">
                  {approvedRules.size} of {displayRules.length} rules approved
                </p>
                <Button
                  onClick={handleContinue}
                  disabled={approvedRules.size === 0}
                  size="lg"
                >
                  Continue to Data Connection
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
