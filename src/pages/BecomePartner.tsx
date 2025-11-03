import { Upload, CheckCircle, Building2, Mail, Phone, Tag, FileText } from 'lucide-react';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface BecomePartnerProps {
  onNavigate: (page: string) => void;
}

export default function BecomePartner({ onNavigate }: BecomePartnerProps) {
  const [formData, setFormData] = useState({
    businessName: '',
    email: '',
    phone: '',
    category: '',
    description: '',
    acceptTerms: false
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  const benefits = [
    {
      title: 'Reach Thousands',
      description: 'Connect with engaged audiences looking for experiences',
      icon: '👥'
    },
    {
      title: 'Easy Management',
      description: 'Powerful tools to manage events, tickets, and attendees',
      icon: '🎯'
    },
    {
      title: 'Get Paid Fast',
      description: 'Instant withdrawals with transparent 7% commission',
      icon: '💰'
    },
    {
      title: 'Analytics & Insights',
      description: 'Track performance with detailed analytics dashboard',
      icon: '📊'
    }
  ];

  const steps = [
    { step: 1, title: 'Apply', description: 'Fill out the registration form' },
    { step: 2, title: 'Review', description: 'We review your application (24 hrs)' },
    { step: 3, title: 'Approved', description: 'Start creating amazing events' }
  ];

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar onNavigate={onNavigate} />
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="bg-white rounded-3xl shadow-xl p-12 text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Application Submitted!</h1>
            <p className="text-xl text-gray-600 mb-8">
              Thank you for your interest in becoming a partner. We'll review your application and get back to you within 24 hours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => onNavigate('landing')}
                className="px-8 py-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-colors"
              >
                Back to Home
              </button>
              <button
                onClick={() => setSubmitted(false)}
                className="px-8 py-4 border-2 border-gray-200 text-gray-700 rounded-xl font-bold hover:border-blue-500 hover:text-blue-600 transition-all"
              >
                Submit Another Application
              </button>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onNavigate={onNavigate} />

      <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Become a Partner
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Join thousands of event organizers using Niko Free to reach engaged audiences and create unforgettable experiences
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-16 mb-20">
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8 md:p-12">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-start space-x-4">
                <div className="text-4xl">{benefit.icon}</div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{benefit.title}</h3>
                  <p className="text-gray-600">{benefit.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p className="text-xl text-gray-600">Simple process to get started</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {steps.map((item, index) => (
            <div key={index} className="relative">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                  {item.step}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-blue-200"></div>
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Partner Application Form</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <Building2 className="w-4 h-4" />
                <span>Business/Brand Name</span>
              </label>
              <input
                type="text"
                required
                value={formData.businessName}
                onChange={(e) => setFormData({ ...formData, businessName: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Enter your business or brand name"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Mail className="w-4 h-4" />
                  <span>Contact Email</span>
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="email@example.com"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Phone className="w-4 h-4" />
                  <span>Phone Number</span>
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="+254 700 000 000"
                />
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <Tag className="w-4 h-4" />
                <span>Primary Category</span>
              </label>
              <select
                required
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors cursor-pointer"
              >
                <option value="">Select a category</option>
                <option value="travel">Travel</option>
                <option value="sports">Sports & Fitness</option>
                <option value="social">Social Activities</option>
                <option value="music">Music & Culture</option>
                <option value="technology">Technology</option>
                <option value="health">Health & Wellbeing</option>
                <option value="pets">Pets & Animals</option>
                <option value="autofest">Autofest</option>
                <option value="hobbies">Hobbies & Interests</option>
                <option value="religious">Religious</option>
                <option value="dance">Dance</option>
                <option value="gaming">Gaming</option>
                <option value="shopping">Shopping</option>
              </select>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <Upload className="w-4 h-4" />
                <span>Logo Upload</span>
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-500 transition-colors cursor-pointer">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 mb-2">Click to upload or drag and drop</p>
                <p className="text-sm text-gray-500">PNG, JPG up to 5MB</p>
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <FileText className="w-4 h-4" />
                <span>Brief Description</span>
              </label>
              <textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors resize-none"
                placeholder="Tell us about your organization and the types of events you plan to host"
              />
            </div>

            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
              <h3 className="font-bold text-gray-900 mb-3">Partner Terms & Conditions</h3>
              <div className="text-sm text-gray-700 space-y-2 mb-4 max-h-40 overflow-y-auto">
                <p>• You agree to pay a 7% commission on all ticket sales</p>
                <p>• All events must comply with local laws and regulations</p>
                <p>• You are responsible for event quality and attendee satisfaction</p>
                <p>• Niko Free reserves the right to remove events that violate guidelines</p>
                <p>• Payment processing takes 2-3 business days</p>
                <p>• You maintain ownership of your event content and data</p>
              </div>
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  required
                  checked={formData.acceptTerms}
                  onChange={(e) => setFormData({ ...formData, acceptTerms: e.target.checked })}
                  className="mt-1 w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  I have read and agree to the Partner Terms & Conditions and Privacy Policy
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={!formData.acceptTerms}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
                formData.acceptTerms
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-xl transform hover:scale-105'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              Submit Application
            </button>
          </form>
        </div>
      </div>

      <Footer />
    </div>
  );
}
