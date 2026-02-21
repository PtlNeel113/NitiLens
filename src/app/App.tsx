import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { Navbar } from './components/Navbar';
import { Login } from './pages/Login';
import { LandingPage } from './pages/LandingPage';
import { PolicyUpload } from './pages/PolicyUpload';
import { DataConnection } from './pages/DataConnection';
import { ComplianceScan } from './pages/ComplianceScan';
import { ReviewQueue } from './pages/ReviewQueue';
import { Dashboard } from './pages/Dashboard';
import { Reports } from './pages/Reports';
import { AMLTransactions } from './pages/AMLTransactions';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login page without navbar */}
        <Route path="/login" element={<Login />} />

        {/* Landing page without navbar */}
        <Route path="/" element={<LandingPage />} />

        {/* App pages with navbar */}
        <Route path="/*" element={
          <div className="min-h-screen bg-gray-50">
            <Navbar />
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/upload" element={<PolicyUpload />} />
              <Route path="/data-connection" element={<DataConnection />} />
              <Route path="/scan" element={<ComplianceScan />} />
              <Route path="/review" element={<ReviewQueue />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/transactions" element={<AMLTransactions />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}
