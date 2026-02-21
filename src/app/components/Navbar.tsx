import { Link, useLocation } from 'react-router';
import { Shield, LayoutDashboard, Upload, FileCheck, AlertCircle, FileText, Table, ChevronDown, Zap, TrendingUp, BarChart3, Database, Activity } from 'lucide-react';
import { useState } from 'react';

export function Navbar() {
  const location = useLocation();
  const [enterpriseOpen, setEnterpriseOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload Policy', icon: Upload },
    { path: '/data-connection', label: 'Data', icon: Table },
    { path: '/scan', label: 'Scan', icon: FileCheck },
    { path: '/transactions', label: 'Transactions', icon: Table },
    { path: '/review', label: 'Review Queue', icon: AlertCircle },
    { path: '/reports', label: 'Reports', icon: FileText }
  ];

  const enterpriseItems = [
    { path: '/enterprise', label: 'Enterprise Overview', icon: Zap },
    { path: '/remediation', label: 'Remediation', icon: Shield },
    { path: '/risk', label: 'Risk Intelligence', icon: TrendingUp },
    { path: '/policy-impact', label: 'Policy Impact', icon: BarChart3 },
    { path: '/connectors', label: 'Connectors', icon: Database },
    { path: '/monitoring', label: 'Monitoring', icon: Activity }
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center gap-2 px-2 text-blue-600">
              <Shield className="w-8 h-8" />
              <span className="font-semibold text-xl">NitiLens</span>
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors ${isActive(item.path)
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
              
              {/* Enterprise Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setEnterpriseOpen(!enterpriseOpen)}
                  className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    enterpriseItems.some(item => isActive(item.path))
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Zap className="w-4 h-4" />
                  Enterprise
                  <ChevronDown className={`w-4 h-4 transition-transform ${enterpriseOpen ? 'rotate-180' : ''}`} />
                </button>
                
                {enterpriseOpen && (
                  <div className="absolute top-full left-0 mt-1 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    {enterpriseItems.map((item) => {
                      const Icon = item.icon;
                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          onClick={() => setEnterpriseOpen(false)}
                          className={`flex items-center gap-3 px-4 py-2 text-sm transition-colors ${
                            isActive(item.path)
                              ? 'bg-blue-50 text-blue-700'
                              : 'text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                          {item.label}
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
