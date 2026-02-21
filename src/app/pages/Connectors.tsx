import { Database, Plus } from 'lucide-react';
import { Card } from '../components/ui/card';

export function Connectors() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Database className="w-8 h-8 text-indigo-600" />
            Data Connectors
          </h1>
          <p className="text-gray-600">
            Connect to PostgreSQL, MySQL, MongoDB, REST APIs, and CSV files
          </p>
        </div>

        <Card className="p-12 text-center">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connector Management</h3>
          <p className="text-gray-600 mb-4">
            Configure and manage your data source connections
          </p>
          <button className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="w-5 h-5" />
            Add Connector
          </button>
        </Card>
      </div>
    </div>
  );
}
