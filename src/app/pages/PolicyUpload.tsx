import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Upload, FileText, CheckCircle, Loader2, Info, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/ui/tooltip';
import { extractedRules } from '../data/mockData';

type Step = 'upload' | 'reading' | 'extracting' | 'review';

export function PolicyUpload() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<Step>('upload');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileName, setFileName] = useState('');
  const [approvedRules, setApprovedRules] = useState<Set<string>>(new Set());

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      simulateUpload();
    }
  };

  const simulateUpload = () => {
    setCurrentStep('reading');
    setUploadProgress(0);
    
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setCurrentStep('extracting'), 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleApproveAll = () => {
    const allIds = new Set(extractedRules.map(rule => rule.id));
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

  const severityColors = {
    critical: 'bg-red-100 text-red-700 border-red-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between max-w-2xl mx-auto">
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep !== 'upload' ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-600'
              }`}>
                {currentStep !== 'upload' ? <CheckCircle className="w-6 h-6" /> : '1'}
              </div>
              <span className="text-sm mt-2">Upload</span>
            </div>
            <div className={`flex-1 h-1 mx-2 ${currentStep === 'upload' ? 'bg-gray-200' : 'bg-blue-600'}`} />
            
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep === 'reading' ? 'bg-blue-600 text-white' : 
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
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep === 'extracting' ? 'bg-blue-600 text-white' : 
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
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep === 'review' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
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
                  <p className="text-xs text-gray-500">PDF files only (MAX. 10MB)</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf"
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

        {/* Reading/Extracting Section */}
        {(currentStep === 'reading' || currentStep === 'extracting') && (
          <Card className="p-8">
            <div className="max-w-md mx-auto text-center">
              <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-6" />
              <h2 className="text-2xl font-bold mb-2">
                {currentStep === 'reading' ? 'Reading Your Policy...' : 'Extracting Compliance Rules...'}
              </h2>
              <p className="text-gray-600 mb-6">
                {currentStep === 'reading' 
                  ? `Processing ${fileName || 'IT Security Policy 2026.pdf'}` 
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
                    <CheckCircle className="w-4 h-4" /> Found 24 pages
                  </p>
                  <p className="text-sm text-green-600 flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4" /> Identified 6 compliance rules
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
                    We found {extractedRules.length} compliance rules in your policy. Review and approve them below.
                  </p>
                </div>
                <Button onClick={handleApproveAll} variant="outline">
                  Approve All
                </Button>
              </div>

              <div className="space-y-4">
                {extractedRules.map((rule) => (
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
                            <Badge className={severityColors[rule.severity]}>
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
                          Source: {rule.sourceReference}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              <div className="mt-8 flex justify-between items-center pt-6 border-t">
                <p className="text-sm text-gray-600">
                  {approvedRules.size} of {extractedRules.length} rules approved
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
