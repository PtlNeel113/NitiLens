import { useNavigate } from 'react-router';
import { Shield, FileText, Database, CheckCircle, TrendingUp, Eye, Users, Zap, ArrowRight, Sparkles, Lock, BarChart3 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-purple-50">
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{
        backgroundImage: 'radial-gradient(circle at 20% 50%, rgb(191 219 254) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgb(243 232 255) 0%, transparent 50%)'
      }}></div>

      <div className="relative z-10">
        <header className="border-b border-gray-200 bg-white/80 backdrop-blur">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <span className="font-bold text-2xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">NitiLens</span>
            </div>
            <div className="flex gap-3">
              <Button onClick={() => navigate('/login')} variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-100">Sign In</Button>
              <Button onClick={() => navigate('/login')} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold">Get Started</Button>
            </div>
          </div>
        </header>

        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 mb-6 bg-blue-100 border border-blue-200 rounded-full px-4 py-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span className="text-sm text-blue-600 font-medium">Compliance Management Platform</span>
            </div>
            <h1 className="text-6xl md:text-7xl font-black mb-6 leading-tight text-gray-900">
              Compliance,<br />
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">Simplified</span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              Automatically extract policies from PDFs, detect violations in real-time, and resolve them with complete audit trails. All with human control.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Button size="lg" onClick={() => navigate('/login')} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold px-10 py-6 text-lg rounded-lg shadow-lg hover:shadow-xl transition duration-300 flex items-center gap-2">
                Request Demo
                <ArrowRight className="w-5 h-5" />
              </Button>
              <Button size="lg" variant="outline" onClick={() => navigate('/login')} className="border-2 border-gray-300 text-gray-700 hover:bg-gray-100 font-bold px-10 py-6 text-lg rounded-lg">View Docs</Button>
            </div>
          </div>
        </section>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-gray-200">          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center"><div className="text-4xl font-bold text-blue-600 mb-2">98%</div><p className="text-gray-600 text-sm">Detection Accuracy</p></div>
            <div className="text-center"><div className="text-4xl font-bold text-blue-600 mb-2">24/7</div><p className="text-gray-600 text-sm">Real-time Monitoring</p></div>
            <div className="text-center"><div className="text-4xl font-bold text-blue-600 mb-2">100%</div><p className="text-gray-600 text-sm">Policy Coverage</p></div>
            <div className="text-center"><div className="text-4xl font-bold text-blue-600 mb-2">SOC 2</div><p className="text-gray-600 text-sm">Type II Certified</p></div>
          </div>
        </div>

        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-200">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">The Compliance Challenge</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">Organizations struggle with policy enforcement while data continuously changes</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-8 border border-gray-200 hover:shadow-lg transition duration-300">
              <div className="bg-red-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4"><FileText className="w-6 h-6 text-red-600" /></div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Unstructured Policies</h3>
              <p className="text-gray-600">Critical rules buried in 50-page PDFs nobody reads</p>
            </Card>
            <Card className="p-8 border border-gray-200 hover:shadow-lg transition duration-300">
              <div className="bg-orange-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4"><Database className="w-6 h-6 text-orange-600" /></div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Constant Change</h3>
              <p className="text-gray-600">Access logs, permissions, and employee records changing every minute</p>
            </Card>
            <Card className="p-8 border border-gray-200 hover:shadow-lg transition duration-300">
              <div className="bg-yellow-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4"><Zap className="w-6 h-6 text-yellow-600" /></div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Manual Chaos</h3>
              <p className="text-gray-600">Teams manually checking spreadsheets instead of running the business</p>
            </Card>
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-200">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">The NitiLens Solution</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">From chaos to clarity in three simple steps</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-8 border border-gray-200 relative hover:shadow-lg transition duration-300 group">
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition duration-300"><FileText className="w-7 h-7 text-white" /></div>
              <div className="absolute top-8 right-8 text-4xl font-bold text-gray-100 group-hover:text-blue-100 transition">1</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Extract & Structure</h3>
              <p className="text-gray-600">Upload PDFs. We automatically extract clear, enforceable rules with full traceability</p>
            </Card>
            <Card className="p-8 border border-gray-200 relative hover:shadow-lg transition duration-300 group">
              <div className="bg-gradient-to-br from-purple-600 to-purple-700 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition duration-300"><Zap className="w-7 h-7 text-white" /></div>
              <div className="absolute top-8 right-8 text-4xl font-bold text-gray-100 group-hover:text-purple-100 transition">2</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Monitor Continuously</h3>
              <p className="text-gray-600">Connect your data sources. We scan continuously and detect violations in real-time</p>
            </Card>
            <Card className="p-8 border border-gray-200 relative hover:shadow-lg transition duration-300 group">
              <div className="bg-gradient-to-br from-green-600 to-green-700 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition duration-300"><CheckCircle className="w-7 h-7 text-white" /></div>
              <div className="absolute top-8 right-8 text-4xl font-bold text-gray-100 group-hover:text-green-100 transition">3</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Review & Resolve</h3>
              <p className="text-gray-600">Review findings with complete context. Resolve with full audit trails visible to regulators</p>
            </Card>
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-200">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Why Choose NitiLens</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">Built for organizations that take compliance seriously</p>
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            <Card className="p-6 border border-gray-200 hover:shadow-lg transition duration-300 text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4"><Eye className="w-6 h-6 text-blue-600" /></div>
              <h3 className="font-bold text-gray-900 mb-2">Explainable</h3>
              <p className="text-sm text-gray-600">Every finding shows evidence and sources for full transparency</p>
            </Card>
            <Card className="p-6 border border-gray-200 hover:shadow-lg transition duration-300 text-center">
              <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4"><Users className="w-6 h-6 text-purple-600" /></div>
              <h3 className="font-bold text-gray-900 mb-2">Human-Controlled</h3>
              <p className="text-sm text-gray-600">Humans make all final decisions - AI assists, humans decide</p>
            </Card>
            <Card className="p-6 border border-gray-200 hover:shadow-lg transition duration-300 text-center">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4"><BarChart3 className="w-6 h-6 text-green-600" /></div>
              <h3 className="font-bold text-gray-900 mb-2">Audit Ready</h3>
              <p className="text-sm text-gray-600">Complete compliance reports with full audit trails</p>
            </Card>
            <Card className="p-6 border border-gray-200 hover:shadow-lg transition duration-300 text-center">
              <div className="bg-orange-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4"><Lock className="w-6 h-6 text-orange-600" /></div>
              <h3 className="font-bold text-gray-900 mb-2">Enterprise Secure</h3>
              <p className="text-sm text-gray-600">SOC 2 Type II certified with encryption at rest</p>
            </Card>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24 border-t border-gray-200">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 md:p-20 text-center text-white">
            <h2 className="text-5xl font-bold mb-4">Stop Guessing About Compliance</h2>
            <p className="text-xl mb-10 max-w-2xl mx-auto opacity-90">Start with a free interactive demo. No credit card required.</p>
            <Button size="lg" onClick={() => navigate('/login')} className="bg-white hover:bg-gray-100 text-blue-600 font-bold px-12 py-6 text-lg rounded-lg shadow-xl hover:shadow-2xl transition duration-300 flex items-center gap-2 mx-auto">
              Get Started Now
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>
        </section>

        <footer className="border-t border-gray-200 py-16 bg-gray-900 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-4 gap-8 mb-12">
              <div>
                <div className="flex items-center gap-2 mb-4"><Shield className="w-5 h-5 text-blue-400" /><span className="font-bold text-lg">NitiLens</span></div>
                <p className="text-gray-400 text-sm">Enterprise compliance management, simplified.</p>
              </div>
              <div>
                <h4 className="font-bold mb-4 text-white">Product</h4>
                <ul className="space-y-2 text-sm text-gray-400"><li><a href="#" className="hover:text-blue-400 transition">Features</a></li><li><a href="#" className="hover:text-blue-400 transition">Pricing</a></li><li><a href="#" className="hover:text-blue-400 transition">Security</a></li></ul>
              </div>
              <div>
                <h4 className="font-bold mb-4 text-white">Company</h4>
                <ul className="space-y-2 text-sm text-gray-400"><li><a href="#" className="hover:text-blue-400 transition">About</a></li><li><a href="#" className="hover:text-blue-400 transition">Blog</a></li><li><a href="#" className="hover:text-blue-400 transition">Contact</a></li></ul>
              </div>
              <div>
                <h4 className="font-bold mb-4 text-white">Legal</h4>
                <ul className="space-y-2 text-sm text-gray-400"><li><a href="#" className="hover:text-blue-400 transition">Privacy</a></li><li><a href="#" className="hover:text-blue-400 transition">Terms</a></li><li><a href="#" className="hover:text-blue-400 transition">Compliance</a></li></ul>
              </div>
            </div>
            <div className="border-t border-gray-700 pt-8 flex justify-between items-center">
              <p className="text-gray-500">© 2026 NitiLens. All rights reserved.</p>
              <div className="flex gap-6 text-gray-500"><a href="#" className="hover:text-blue-400 transition">Twitter</a><a href="#" className="hover:text-blue-400 transition">LinkedIn</a><a href="#" className="hover:text-blue-400 transition">GitHub</a></div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
