import { Link, useLocation } from 'react-router';
import { Shield, LayoutDashboard, Upload, FileCheck, AlertCircle, FileText, Table } from 'lucide-react';

export function Navbar() {
  const location = useLocation();

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
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
