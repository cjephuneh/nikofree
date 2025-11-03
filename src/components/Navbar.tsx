import { Calendar, Menu, X, LogIn } from 'lucide-react';
import { useState } from 'react';

interface NavbarProps {
  onNavigate: (page: string) => void;
  currentPage?: string;
}

export default function Navbar({ onNavigate, currentPage = 'landing' }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <button
              onClick={() => onNavigate('landing')}
              className="flex items-center space-x-2"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center transform hover:scale-105 transition-transform">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                Niko Free
              </span>
            </button>

            <div className="hidden md:flex space-x-1">
              <button
                onClick={() => onNavigate('landing')}
                className={`px-4 py-2 font-medium transition-colors ${
                  currentPage === 'landing' 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => onNavigate('about')}
                className={`px-4 py-2 font-medium transition-colors ${
                  currentPage === 'about' 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                About Us
              </button>
              <button
                onClick={() => onNavigate('this-weekend')}
                className={`px-4 py-2 font-medium transition-colors ${
                  currentPage === 'this-weekend' 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                This Weekend
              </button>
              <button
                onClick={() => onNavigate('calendar')}
                className={`px-4 py-2 font-medium transition-colors ${
                  currentPage === 'calendar' 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                Calendar
              </button>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <button
              onClick={() => onNavigate('become-partner')}
              className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg font-medium transition-colors"
            >
              Become a Partner
            </button>
            <button
              onClick={() => onNavigate('user-dashboard')}
              className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-medium hover:shadow-lg transform hover:scale-105 transition-all"
            >
              <LogIn className="w-4 h-4" />
              <span>Log In / Sign Up</span>
            </button>
          </div>

          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-700" />
            ) : (
              <Menu className="w-6 h-6 text-gray-700" />
            )}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-4 py-3 space-y-2">
            <button
              onClick={() => { onNavigate('landing'); setMobileMenuOpen(false); }}
              className={`block w-full text-left px-4 py-2 rounded-lg ${
                currentPage === 'landing' 
                  ? 'bg-blue-50 text-blue-600 font-semibold' 
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => { onNavigate('about'); setMobileMenuOpen(false); }}
              className={`block w-full text-left px-4 py-2 rounded-lg ${
                currentPage === 'about' 
                  ? 'bg-blue-50 text-blue-600 font-semibold' 
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              About Us
            </button>
            <button
              onClick={() => { onNavigate('this-weekend'); setMobileMenuOpen(false); }}
              className={`block w-full text-left px-4 py-2 rounded-lg ${
                currentPage === 'this-weekend' 
                  ? 'bg-blue-50 text-blue-600 font-semibold' 
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              This Weekend
            </button>
            <button
              onClick={() => { onNavigate('calendar'); setMobileMenuOpen(false); }}
              className={`block w-full text-left px-4 py-2 rounded-lg ${
                currentPage === 'calendar' 
                  ? 'bg-blue-50 text-blue-600 font-semibold' 
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              Calendar
            </button>
            <button
              onClick={() => { onNavigate('become-partner'); setMobileMenuOpen(false); }}
              className="block w-full text-left px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg font-medium"
            >
              Become a Partner
            </button>
            <button
              onClick={() => { onNavigate('user-dashboard'); setMobileMenuOpen(false); }}
              className="block w-full px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium"
            >
              Log In / Sign Up
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
