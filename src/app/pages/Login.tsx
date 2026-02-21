import { useNavigate } from 'react-router';
import { Shield, Mail, ArrowRight, CheckCircle, Lock, Zap, Users, BarChart3 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { useState } from 'react';

export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setIsLoading(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 500);
    }
  };

  const handleGoogleLogin = () => {
    setIsLoading(true);
    setTimeout(() => {
      navigate('/dashboard');
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-30 pointer-events-none" style={{
        backgroundImage: 'radial-gradient(circle at 20% 50%, rgb(191 219 254) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgb(243 232 255) 0%, transparent 50%)'
      }}></div>

      <div className="relative z-10 min-h-screen grid grid-cols-1 lg:grid-cols-2 gap-0">
        {/* Left Side - Info (Desktop Only) */}
        <div className="hidden lg:flex flex-col justify-between bg-gradient-to-br from-blue-600 to-purple-700 p-12 text-white">
          <div>
            <div className="flex items-center gap-3 mb-12">
              <div className="bg-white/25 backdrop-blur-sm p-3 rounded-xl shadow-lg hover:bg-white/35 transition-all duration-300">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <span className="font-bold text-3xl tracking-tight">NitiLens</span>
            </div>
            
            <div className="mb-16">
              <h1 className="text-5xl font-bold mb-6 leading-tight">
                Compliance Simplified
              </h1>
              <p className="text-xl text-blue-100 mb-10">
                Detect policy violations before they become audit findings. With complete transparency and human control.
              </p>
            </div>

            {/* Benefits */}
            <div className="space-y-6">
              <div className="flex gap-4 items-start group hover:translate-x-1 transition-transform duration-300">
                <div className="bg-white/20 p-2.5 rounded-lg group-hover:bg-white/30 transition-all duration-300">
                  <CheckCircle className="w-5 h-5 text-green-300 flex-shrink-0" />
                </div>
                <div>
                  <h3 className="font-bold text-base mb-1 leading-tight">Real-time Monitoring</h3>
                  <p className="text-blue-100 text-sm">24/7 continuous violation detection</p>
                </div>
              </div>
              
              <div className="flex gap-4 items-start group hover:translate-x-1 transition-transform duration-300">
                <div className="bg-white/20 p-2.5 rounded-lg group-hover:bg-white/30 transition-all duration-300">
                  <Zap className="w-5 h-5 text-yellow-300 flex-shrink-0" />
                </div>
                <div>
                  <h3 className="font-bold text-base mb-1 leading-tight">Instant Insights</h3>
                  <p className="text-blue-100 text-sm">AI-powered analysis with explainability</p>
                </div>
              </div>
              
              <div className="flex gap-4 items-start group hover:translate-x-1 transition-transform duration-300">
                <div className="bg-white/20 p-2.5 rounded-lg group-hover:bg-white/30 transition-all duration-300">
                  <Lock className="w-5 h-5 text-blue-200 flex-shrink-0" />
                </div>
                <div>
                  <h3 className="font-bold text-base mb-1 leading-tight">Enterprise Security</h3>
                  <p className="text-blue-100 text-sm">SOC 2 Type II compliant, encrypted</p>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Stats */}
          <div className="pt-8 border-t border-white/20">
            <div className="grid grid-cols-3 gap-8">
              <div>
                <div className="text-4xl font-bold mb-2">98%</div>
                <p className="text-sm text-blue-100">Detection Rate</p>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">24/7</div>
                <p className="text-sm text-blue-100">Monitoring</p>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">10k+</div>
                <p className="text-sm text-blue-100">Scans/day</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="flex flex-col items-center justify-center px-6 lg:px-12 py-12 lg:py-0 bg-gradient-to-br from-purple-50 via-blue-50 to-white">
          {/* Mobile Header */}
          <div className="lg:hidden w-full mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <span className="font-bold text-2xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">NitiLens</span>
            </div>
          </div>

          <div className="w-full max-w-md">
            <div className="mb-10">
              <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3 leading-tight">Welcome Back</h2>
              <p className="text-gray-600 text-base">Sign in to your compliance dashboard</p>
            </div>

            {/* Login Card */}
            <Card className="bg-white/85 backdrop-blur-sm border border-blue-200/40 rounded-2xl shadow-lg p-8 mb-7 hover:shadow-2xl hover:border-blue-300/60 transition-all duration-300">
              {/* Email Login */}
              <form onSubmit={handleEmailLogin} className="mb-7">
                <label className="block text-sm font-semibold text-gray-700 mb-2.5">
                  Email Address
                </label>
                <div className="relative mb-6">
                  <Mail className="absolute left-4 top-3.5 w-5 h-5 text-blue-500" />
                  <Input
                    type="email"
                    placeholder="you@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-12 bg-blue-50/70 border border-blue-200 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/40 h-12 rounded-lg transition-all duration-300 focus:bg-blue-50 text-base font-medium"
                    disabled={isLoading}
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-3 rounded-lg transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 text-base h-12"
                  disabled={!email || isLoading}
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      Signing in...
                    </>
                  ) : (
                    <>
                      Continue with Email
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </Button>
              </form>

              {/* Divider */}
              <div className="relative my-7">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-blue-200/40"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-3 bg-white/85 text-gray-500 font-semibold text-xs uppercase tracking-wider">OR</span>
                </div>
              </div>

              {/* Google Login */}
              <Button
                onClick={handleGoogleLogin}
                className="w-full flex items-center justify-center gap-3 py-3 bg-white hover:bg-blue-50 border border-blue-200 hover:border-blue-400 text-gray-900 font-semibold rounded-lg transition-all duration-300 text-base h-12 hover:shadow-md hover:scale-105 active:scale-95"
                disabled={isLoading}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                {isLoading ? 'Signing in...' : 'Continue with Google'}
              </Button>
            </Card>

            {/* Footer */}
            <div className="text-center text-sm text-gray-600 mt-8">
              <p>
                Don't have an account?{' '}
                <button className="text-blue-600 hover:text-blue-700 font-semibold transition duration-300 hover:underline">
                  Sign up here
                </button>
              </p>
            </div>

            {/* Security badge */}
            <div className="mt-8 text-center text-xs text-gray-500 flex items-center justify-center gap-2 pb-2">
              <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              <span className="text-gray-600 font-medium">Enterprise-grade security</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
