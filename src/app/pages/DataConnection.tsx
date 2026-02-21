import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Database, CheckCircle, ArrowRight, Table, ExternalLink, Lock, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { api, type Dataset, type AMLStats } from '../services/api';

interface DatasetOption extends Dataset {
  records: number;
  domain: string;
  color: string;
  status: 'connected' | 'available';
}

export function DataConnection() {
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState<DatasetOption[]>([]);
  const [amlStats, setAmlStats] = useState<AMLStats | null>(null);
  const [amlPreview, setAmlPreview] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [mappingComplete, setMappingComplete] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [list, stats, preview] = await Promise.all([
          api.listDatasets(),
          api.getAMLStats(),
          api.getAMLPreview(4)
        ]);

        const enhanced: DatasetOption[] = list.map(d => ({
          ...d,
          records: d.id === 'ibm-aml' ? stats.total_transactions : 6300000,
          domain: d.id === 'ibm-aml' ? 'Anti-Money Laundering' : 'Fraud Detection',
          color: d.id === 'ibm-aml' ? 'blue' : 'purple',
          status: d.connected ? 'connected' : 'available'
        } as any));

        setDatasets(enhanced);
        setAmlStats(stats);

        const mapped = preview.rows.map((r: any) => ({
          id: r.id ?? 'TXN-' + Math.random().toString(36).substr(2, 9).toUpperCase(),
          timestamp: r.Timestamp,
          fromBank: r['From Bank'],
          toBank: r['To Bank'],
          amountPaid: r['Amount Paid'],
          paymentCurrency: r['Payment Currency'],
          paymentFormat: r['Payment Format'],
          isLaundering: r['Is Laundering']
        }));
        setAmlPreview(mapped);
      } catch (e) {
        console.error('Failed to load connection data:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSelectDataset = (datasetId: string) => {
    setSelectedDataset(datasetId);
    setTimeout(() => {
      setMappingComplete(true);
    }, 1400);
  };

  const handleContinue = () => {
    navigate('/scan');
  };

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
          <h1 className="text-3xl font-bold mb-2">Data Connections</h1>
          <p className="text-gray-600">
            Connect financial transaction datasets to scan for AML compliance violations
          </p>
        </div>

        {!selectedDataset && (
          <div className="grid md:grid-cols-3 gap-6">
            {datasets.map((dataset) => (
              <Card
                key={dataset.id}
                className={`p-6 cursor-pointer transition-all hover:shadow-lg ${dataset.status === 'connected'
                  ? 'border-blue-400 bg-blue-50/40 hover:border-blue-500'
                  : 'hover:border-gray-400'
                  }`}
                onClick={() => handleSelectDataset(dataset.id)}
              >
                <div className="flex items-start justify-between mb-4">
                  <Database className={`w-10 h-10 text-${dataset.color}-600`} />
                  <Badge className={
                    dataset.status === 'connected'
                      ? 'bg-green-100 text-green-700 border-green-300'
                      : 'bg-gray-100 text-gray-600'
                  }>
                    {dataset.status === 'connected' ? '● Connected' : 'Available'}
                  </Badge>
                </div>
                <h3 className="text-lg font-semibold mb-2">{dataset.name}</h3>
                <p className="text-sm text-gray-600 mb-4">{dataset.description}</p>
                <div className="space-y-1 text-sm text-gray-500 mb-4">
                  <p>📊 {dataset.records.toLocaleString()}+ records</p>
                  <p>🏷️ {dataset.domain}</p>
                  <p>📄 {dataset.license}</p>
                </div>
                <Button
                  className="w-full"
                  variant={dataset.status === 'connected' ? 'default' : 'outline'}
                >
                  {dataset.status === 'connected' ? 'View Connection' : 'Connect Dataset'}
                </Button>
              </Card>
            ))}
          </div>
        )}

        {selectedDataset && !mappingComplete && (
          <Card className="p-8">
            <div className="text-center">
              <Database className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-pulse" />
              <h2 className="text-2xl font-bold mb-2">Connecting to IBM AML Dataset...</h2>
              <p className="text-gray-600">Mapping schema fields to AML compliance rule conditions</p>
              <div className="mt-6 space-y-2 text-sm text-left max-w-md mx-auto bg-gray-50 rounded-lg p-4">
                <p className="text-green-600 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Loading sample_transactions.csv...
                </p>
                <p className="text-green-600 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Validating schema (11 columns)...
                </p>
                <p className="text-blue-600 flex items-center gap-2 animate-pulse">
                  <Database className="w-4 h-4" /> Mapping fields to rule conditions...
                </p>
              </div>
            </div>
          </Card>
        )}

        {selectedDataset && mappingComplete && (
          <div className="space-y-6">
            <Card className="p-6 bg-green-50 border-green-200">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div className="flex-1">
                  <h3 className="font-semibold text-green-900">Connection Successful — IBM AML Transaction Dataset</h3>
                  <p className="text-sm text-green-700">
                    Loaded {amlStats?.total_transactions ?? 0} transactions · {amlStats?.confirmed_laundering ?? 0} labeled as laundering ·{' '}
                    {Object.keys(amlStats?.top_currencies ?? {}).length} currencies · {Object.keys(amlStats?.payment_formats ?? {}).length} payment formats
                  </p>
                </div>
                <a
                  href="https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-700 hover:text-green-900"
                >
                  <ExternalLink className="w-5 h-5" />
                </a>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-xl font-semibold mb-4">Schema Field Mapping</h3>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">AML Rule Condition Field</p>
                  <div className="space-y-2">
                    {[
                      'Amount Paid',
                      'Payment Currency',
                      'Receiving Currency',
                      'Is Laundering',
                      'From Account',
                      'Payment Format'
                    ].map(field => (
                      <div key={field} className="p-2 bg-blue-50 rounded text-sm font-mono">{field}</div>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">CSV Column</p>
                  <div className="space-y-2">
                    {[
                      'Amount Paid',
                      'Payment Currency',
                      'Receiving Currency',
                      'Is Laundering',
                      'Account',
                      'Payment Format'
                    ].map(col => (
                      <div key={col} className="p-2 bg-green-50 border border-green-200 rounded text-sm flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                        <span className="font-mono">{col}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Data Preview Table */}
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-2 border-b flex items-center justify-between">
                  <h4 className="font-medium flex items-center gap-2">
                    <Table className="w-4 h-4" />
                    Transaction Preview (first 4 rows)
                  </h4>
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Lock className="w-3 h-3" /> CDLA-Sharing-1.0
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-3 py-2 text-left">ID</th>
                        <th className="px-3 py-2 text-left">Timestamp</th>
                        <th className="px-3 py-2 text-left">From→To Bank</th>
                        <th className="px-3 py-2 text-right">Amount Paid</th>
                        <th className="px-3 py-2 text-left">Currency</th>
                        <th className="px-3 py-2 text-left">Format</th>
                        <th className="px-3 py-2 text-center">Laundering</th>
                      </tr>
                    </thead>
                    <tbody>
                      {amlPreview.map((txn) => (
                        <tr
                          key={txn.id}
                          className={`border-t ${txn.isLaundering === 1 ? 'bg-red-50' : ''}`}
                        >
                          <td className="px-3 py-2 font-mono">{txn.id}</td>
                          <td className="px-3 py-2 text-gray-600">{txn.timestamp}</td>
                          <td className="px-3 py-2">Bank {txn.fromBank} → {txn.toBank}</td>
                          <td className="px-3 py-2 text-right font-mono">
                            ${txn.amountPaid.toLocaleString()}
                          </td>
                          <td className="px-3 py-2">{txn.paymentCurrency}</td>
                          <td className="px-3 py-2">{txn.paymentFormat}</td>
                          <td className="px-3 py-2 text-center">
                            {txn.isLaundering === 1
                              ? <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-semibold">YES</span>
                              : <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">No</span>
                            }
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="mt-6 flex justify-between items-center pt-4 border-t">
                <button
                  onClick={() => { setSelectedDataset(''); setMappingComplete(false); }}
                  className="text-sm text-gray-500 hover:underline"
                >
                  ← Back to datasets
                </button>
                <Button onClick={handleContinue} size="lg">
                  Continue to Scan
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
