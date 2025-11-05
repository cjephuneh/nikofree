import { X } from 'lucide-react';
import { useState } from 'react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (page: string) => void;
  onSwitchToSignup?: () => void;
}

export default function LoginModal({ isOpen, onClose, onNavigate, onSwitchToSignup }: LoginModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [keepLoggedIn, setKeepLoggedIn] = useState(false);

  if (!isOpen) return null;

  const handleSignup = () => {
    onClose();
    if (onSwitchToSignup) {
      onSwitchToSignup();
    } else {
      onNavigate('signup');
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Login with:', { email, password, keepLoggedIn });
    
    // Navigate to user dashboard
    onClose();
    onNavigate('user-dashboard');
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        ></div>

        {/* Center modal */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors z-10"
          >
            <X className="w-6 h-6" />
          </button>

          <div className="bg-white px-8 pt-8 pb-6">
            {/* Title */}
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Log in</h2>

            {/* Social login buttons */}
            <div className="space-y-3 mb-6">
              <button className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors">
                <img
                  src="https://www.google.com/favicon.ico"
                  alt="Google"
                  className="w-5 h-5"
                />
                <span className="font-medium text-gray-700">Log in with Google</span>
              </button>

              <button className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                </svg>
                <span className="font-medium text-gray-700">Log in with Apple</span>
              </button>
            </div>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">or</span>
              </div>
            </div>

            {/* Email/Password form */}
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:border-transparent outline-none transition-all"
                  onFocus={(e) => {
                    e.target.style.borderColor = '#27aae2';
                    e.target.style.boxShadow = '0 0 0 3px rgba(39, 170, 226, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#d1d5db';
                    e.target.style.boxShadow = 'none';
                  }}
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:border-transparent outline-none transition-all"
                  onFocus={(e) => {
                    e.target.style.borderColor = '#27aae2';
                    e.target.style.boxShadow = '0 0 0 3px rgba(39, 170, 226, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#d1d5db';
                    e.target.style.boxShadow = 'none';
                  }}
                  placeholder="Enter your password"
                  required
                />
              </div>

              {/* Keep me logged in */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="keepLoggedIn"
                  checked={keepLoggedIn}
                  onChange={(e) => setKeepLoggedIn(e.target.checked)}
                  className="w-4 h-4 border-gray-300 rounded"
                  style={{ accentColor: '#27aae2' }}
                />
                <label htmlFor="keepLoggedIn" className="ml-2 text-sm text-gray-700">
                  Keep me logged in
                </label>
              </div>

              {/* Login button */}
              <button
                type="submit"
                className="w-full px-4 py-3 text-white rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all"
                style={{ background: 'linear-gradient(to right, #27aae2, #1a8ec4)' }}
              >
                Log in
              </button>
            </form>

            {/* Forgot password */}
            <div className="mt-4 text-center">
              <button 
                className="text-sm font-medium transition-colors"
                style={{ color: '#27aae2' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#1a8ec4'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#27aae2'}
              >
                Forgot password?
              </button>
            </div>

            {/* Help link */}
            <div className="mt-2 text-center">
              <button className="text-gray-600 text-sm hover:text-gray-700 transition-colors">
                Issues with login? Get help
              </button>
            </div>

            {/* Signup link */}
            <div className="mt-6 text-center">
              <span className="text-gray-600">Do not have an account yet? </span>
              <button
                onClick={handleSignup}
                className="font-medium transition-colors"
                style={{ color: '#27aae2' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#1a8ec4'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#27aae2'}
              >
                Sign up
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
