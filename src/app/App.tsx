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
import { Remediation } from './pages/Remediation';
import { Risk } from './pages/Risk';
import { PolicyImpact } from './pages/PolicyImpact';
import { Connectors } from './pages/Connectors';
import { Monitoring } from './pages/Monitoring';
import { EnterpriseControlCenter } from './pages/EnterpriseControlCenter';
import Subscription from './pages/Subscription';
import { NitiGuardChat } from './components/NitiGuardChat';

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

              {/* Enterprise Control Center */}
              <Route path="/enterprise" element={<EnterpriseControlCenter />} />

              {/* Enterprise Features */}
              <Route path="/remediation" element={<Remediation />} />
              <Route path="/risk" element={<Risk />} />
              <Route path="/policy-impact" element={<PolicyImpact />} />
              <Route path="/connectors" element={<Connectors />} />
              <Route path="/monitoring" element={<Monitoring />} />
              <Route path="/subscription" element={<Subscription />} />
              <Route path="/alerts" element={<Dashboard />} />
              <Route path="/settings" element={<Dashboard />} />

              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
            <NitiGuardChat />
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}
