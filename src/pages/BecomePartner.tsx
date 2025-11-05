import { Upload, CheckCircle, Building2, Mail, Phone, Tag, FileText, ArrowRight, ArrowLeft, MapPin, PenTool, Plus, Minus } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface BecomePartnerProps {
  onNavigate: (page: string) => void;
}

export default function BecomePartner({ onNavigate }: BecomePartnerProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    businessName: '',
    logo: null as File | null,
    location: '',
    categories: [] as string[],
    interests: '',
    email: '',
    phone: '',
    signature: '',
    acceptTerms: false
  });
  const [submitted, setSubmitted] = useState(false);
  const [locationSuggestions, setLocationSuggestions] = useState<any[]>([]);
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false);
  const locationTimeoutRef = useRef<NodeJS.Timeout>();
  const [emailError, setEmailError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [customInterest, setCustomInterest] = useState('');
  const [customInterests, setCustomInterests] = useState<string[]>([]);

  const categories = [
    { id: 'travel', name: 'Travel' },
    { id: 'sports', name: 'Sports & Fitness' },
    { id: 'social', name: 'Social Activities' },
    { id: 'music', name: 'Music & Culture' },
    { id: 'health', name: 'Health & Wellbeing' },
    { id: 'pets', name: 'Pets & Animals' },
    { id: 'autofest', name: 'Autofest' },
    { id: 'hobbies', name: 'Hobbies & Interests' },
    { id: 'gaming', name: 'Gaming' },
    { id: 'shopping', name: 'Shopping' },
    { id: 'religious', name: 'Religious' },
    { id: 'dance', name: 'Dance' },
  ];

  const handleCategoryToggle = (categoryId: string) => {
    setFormData(prev => ({
      ...prev,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter(id => id !== categoryId)
        : [...prev.categories, categoryId]
    }));
  };

  const handleNext = () => {
    setCurrentStep(prev => Math.min(prev + 1, 5));
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = () => {
    setSubmitted(true);
  };

  // Auto-detect user's location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
            );
            const data = await response.json();
            const city = data.address.city || data.address.town || data.address.village || data.address.county;
            if (city) {
              setFormData(prev => ({ ...prev, location: city }));
            }
          } catch (error) {
            console.error('Error fetching location:', error);
            setFormData(prev => ({ ...prev, location: 'Nairobi' }));
          }
        },
        (error) => {
          console.error('Geolocation error:', error);
          setFormData(prev => ({ ...prev, location: 'Nairobi' }));
        }
      );
    } else {
      setFormData(prev => ({ ...prev, location: 'Nairobi' }));
    }
  }, []);

  // Fetch location suggestions
  const fetchLocationSuggestions = async (query: string) => {
    if (query.length < 3) {
      setLocationSuggestions([]);
      setShowLocationSuggestions(false);
      return;
    }

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=ke`
      );
      const data = await response.json();
      setLocationSuggestions(data);
      setShowLocationSuggestions(true);
    } catch (error) {
      console.error('Error fetching location suggestions:', error);
    }
  };

  const handleLocationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData({ ...formData, location: value });

    if (locationTimeoutRef.current) {
      clearTimeout(locationTimeoutRef.current);
    }

    locationTimeoutRef.current = setTimeout(() => {
      fetchLocationSuggestions(value);
    }, 300);
  };

  const handleLocationSelect = (location: any) => {
    const locationName = location.display_name.split(',')[0];
    setFormData({ ...formData, location: locationName });
    setShowLocationSuggestions(false);
    setLocationSuggestions([]);
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setEmailError('Email is required');
      return false;
    }
    if (!emailRegex.test(email)) {
      setEmailError('Please enter a valid email address');
      return false;
    }
    setEmailError('');
    return true;
  };

  const validatePhone = (phone: string) => {
    // Kenyan phone number format: +254 or 0 followed by 9 digits
    const phoneRegex = /^(\+254|0)[17]\d{8}$/;
    if (!phone) {
      setPhoneError('Phone number is required');
      return false;
    }
    if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
      setPhoneError('Please enter a valid Kenyan phone number (e.g., +254 700 000 000 or 0700 000 000)');
      return false;
    }
    setPhoneError('');
    return true;
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData({ ...formData, email: value });
    if (value) {
      validateEmail(value);
    }
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData({ ...formData, phone: value });
    if (value) {
      validatePhone(value);
    }
  };

  const handleAddCustomInterest = () => {
    if (customInterest.trim() && !customInterests.includes(customInterest.trim())) {
      setCustomInterests([...customInterests, customInterest.trim()]);
      setCustomInterest('');
    }
  };

  const handleRemoveCustomInterest = (interest: string) => {
    setCustomInterests(customInterests.filter(i => i !== interest));
  };

  const handleCustomInterestKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddCustomInterest();
    }
  };

  const canProceedStep1 = formData.businessName && formData.location;
  const canProceedStep2 = formData.categories.length > 0;
  const canProceedStep3 = formData.email && formData.phone && !emailError && !phoneError;
  const canProceedStep4 = formData.signature && formData.acceptTerms;

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
            <p className="text-xl text-gray-600 mb-4">
              Thank you for your interest in becoming a partner.
            </p>
            <div className="rounded-xl p-6 mb-8" style={{ backgroundColor: '#e6f7ff', borderWidth: '2px', borderStyle: 'solid', borderColor: '#27aae2' }}>
              <p className="text-lg font-semibold mb-2" style={{ color: '#1a8ec4' }}>What's Next?</p>
              <p className="text-gray-700">
                Our admin team will review your application within 24 hours. You'll receive an email at <strong>{formData.email}</strong> with the approval status.
              </p>
            </div>
            <button
              onClick={() => onNavigate('landing')}
              className="px-8 py-4 text-white rounded-xl font-bold transition-colors"
              style={{ backgroundColor: '#27aae2' }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
            >
              Back to Home
            </button>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 relative">
      {/* Light mode dot pattern overlay */}
      <div className="block dark:hidden fixed inset-0 pointer-events-none z-0" style={{
        backgroundImage: 'radial-gradient(circle, rgba(0, 0, 0, 0.08) 1px, transparent 1px)',
        backgroundSize: '30px 30px'
      }}></div>
      
      {/* Dark mode dot pattern overlay */}
      <div className="hidden dark:block fixed inset-0 pointer-events-none z-0" style={{
        backgroundImage: 'radial-gradient(circle, rgba(156, 163, 175, 0.15) 1px, transparent 1px)',
        backgroundSize: '30px 30px'
      }}></div>
      
      <div className="relative z-10">
        <Navbar onNavigate={onNavigate} />

      <div className="py-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 text-center">
            Become a Partner
          </h1>
          <p className="text-lg text-gray-600 text-center mb-8">
            Join thousands of event organizers using Niko Free
          </p>
          
          {/* Progress Steps */}
          <div className="max-w-md mx-auto">
            <div className="flex items-center">
              {[1, 2, 3, 4].map((step) => (
                <div key={step} className="flex items-center flex-1">
                  <div
                    className={`h-2.5 flex-1 transition-all ${
                      currentStep >= step ? 'bg-gray-300' : 'bg-gray-300'
                    } ${
                      step === 1 ? 'rounded-l-full' : 
                      step === 4 ? 'rounded-r-full' : ''
                    }`}
                    style={currentStep >= step ? { backgroundColor: '#27aae2' } : {}}
                  />
                  {step < 4 && <div className="w-2" />}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 mt-1 mb-3">
        <div className="p-8 md:p-12">
          
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Basic Information</h2>
                <p className="text-gray-600">Tell us about your business</p>
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Building2 className="w-4 h-4" />
                  <span>Business/Brand Name *</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.businessName}
                  onChange={(e) => setFormData({ ...formData, businessName: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none transition-colors"
                  style={{ borderColor: formData.businessName ? '#27aae2' : '' }}
                  onFocus={(e) => e.target.style.borderColor = '#27aae2'}
                  onBlur={(e) => { if (!formData.businessName) e.target.style.borderColor = ''; }}
                  placeholder="Enter your business or brand name"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Upload className="w-4 h-4" />
                  <span>Logo Upload</span>
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center transition-colors cursor-pointer"
                  style={{ borderColor: formData.logo ? '#27aae2' : '' }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = '#27aae2'}
                  onMouseLeave={(e) => { if (!formData.logo) e.currentTarget.style.borderColor = ''; }}
                >
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 mb-2">Click to upload or drag and drop</p>
                  <p className="text-sm text-gray-500">PNG, JPG up to 5MB</p>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => setFormData({ ...formData, logo: e.target.files?.[0] || null })}
                  />
                </div>
              </div>

              <div className="relative">
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <MapPin className="w-4 h-4" />
                  <span>Location *</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={handleLocationChange}
                  onFocus={(e) => { 
                    if (formData.location.length >= 3) setShowLocationSuggestions(true);
                    e.target.style.borderColor = '#27aae2';
                  }}
                  onBlur={(e) => { if (!formData.location) e.target.style.borderColor = ''; }}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none transition-colors"
                  style={{ borderColor: formData.location ? '#27aae2' : '' }}
                  placeholder="Search for your location..."
                />
                {showLocationSuggestions && locationSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-2 bg-white border-2 border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                    {locationSuggestions.map((location, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => handleLocationSelect(location)}
                        className="w-full px-4 py-3 text-left transition-colors flex items-start space-x-2 border-b border-gray-100 last:border-b-0"
                        style={{ backgroundColor: 'white' }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e6f7ff'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                      >
                        <MapPin className="w-4 h-4 mt-1 flex-shrink-0" style={{ color: '#27aae2' }} />
                        <span className="text-sm text-gray-900">{location.display_name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex justify-end pt-4">
                <button
                  onClick={handleNext}
                  disabled={!canProceedStep1}
                  className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center space-x-2 ${
                    canProceedStep1
                      ? 'text-white hover:opacity-90'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  style={canProceedStep1 ? { backgroundColor: '#27aae2' } : {}}
                >
                  <span>Next</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Categories & Interests */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Categories & Interests</h2>
                <p className="text-gray-600">What type of events will you organize?</p>
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-4">
                  <Tag className="w-4 h-4" />
                  <span>Select Categories * (Choose at least one)</span>
                </label>
                <div className="flex flex-wrap gap-3">
                  {categories.map((category) => {
                    const isSelected = formData.categories.includes(category.id);
                    return (
                      <button
                        key={category.id}
                        type="button"
                        onClick={() => handleCategoryToggle(category.id)}
                        className={`px-4 py-2 rounded-full border-2 transition-all flex items-center space-x-2 ${
                          isSelected
                            ? 'text-white'
                            : 'border-gray-200 bg-white text-gray-900'
                        }`}
                        style={isSelected ? { 
                          borderColor: '#27aae2', 
                          backgroundColor: '#27aae2' 
                        } : {}}
                        onMouseEnter={(e) => {
                          if (!isSelected) e.currentTarget.style.borderColor = '#27aae2';
                        }}
                        onMouseLeave={(e) => {
                          if (!isSelected) e.currentTarget.style.borderColor = '';
                        }}
                      >
                        <span className="text-sm font-medium">{category.name}</span>
                        {isSelected ? (
                          <Minus className="w-4 h-4 flex-shrink-0" />
                        ) : (
                          <Plus className="w-4 h-4 flex-shrink-0" />
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <FileText className="w-4 h-4" />
                  <span>Additional Interests (Optional)</span>
                </label>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={customInterest}
                    onChange={(e) => setCustomInterest(e.target.value)}
                    onKeyPress={handleCustomInterestKeyPress}
                    className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-xl focus:outline-none transition-colors text-sm"
                    onFocus={(e) => e.target.style.borderColor = '#27aae2'}
                    onBlur={(e) => e.target.style.borderColor = ''}
                    placeholder="Type an interest and press Enter or click Add"
                  />
                  <button
                    type="button"
                    onClick={handleAddCustomInterest}
                    className="px-6 py-2 text-white rounded-xl font-medium hover:opacity-90 transition-colors text-sm"
                    style={{ backgroundColor: '#27aae2' }}
                  >
                    Add
                  </button>
                </div>
                {customInterests.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {customInterests.map((interest, index) => (
                      <div
                        key={index}
                        className="px-4 py-2 rounded-full border-2 text-white flex items-center space-x-2"
                        style={{ borderColor: '#000000', backgroundColor: '#000000' }}
                      >
                        <span className="text-sm font-medium">{interest}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveCustomInterest(interest)}
                          className="hover:bg-gray-800 rounded-full p-0.5 transition-colors"
                        >
                          <Minus className="w-4 h-4 flex-shrink-0" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex justify-between pt-4">
                <button
                  onClick={handlePrevious}
                  className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-bold transition-all flex items-center space-x-2"
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#27aae2';
                    e.currentTarget.style.color = '#27aae2';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '';
                    e.currentTarget.style.color = '';
                  }}
                >
                  <ArrowLeft className="w-5 h-5" />
                  <span>Back</span>
                </button>
                <button
                  onClick={handleNext}
                  disabled={!canProceedStep2}
                  className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center space-x-2 ${
                    canProceedStep2
                      ? 'text-white hover:opacity-90'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  style={canProceedStep2 ? { backgroundColor: '#27aae2' } : {}}
                >
                  <span>Next</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Contact Details */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Contact Details</h2>
                <p className="text-gray-600">How can we reach you?</p>
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Mail className="w-4 h-4" />
                  <span>Email to Receive RSVPs *</span>
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleEmailChange}
                  onBlur={() => formData.email && validateEmail(formData.email)}
                  className={`w-full px-4 py-3 border-2 rounded-xl focus:outline-none transition-colors ${
                    emailError 
                      ? 'border-red-500 focus:border-red-500' 
                      : 'border-gray-200'
                  }`}
                  onFocus={(e) => { if (!emailError) e.target.style.borderColor = '#27aae2'; }}
                  onBlur={(e) => { 
                    if (formData.email) validateEmail(formData.email);
                    if (!emailError && !formData.email) e.target.style.borderColor = '';
                  }}
                  placeholder="email@example.com"
                />
                {emailError && (
                  <p className="text-sm text-red-600 mt-1 flex items-center space-x-1">
                    <span>⚠</span>
                    <span>{emailError}</span>
                  </p>
                )}
                {!emailError && formData.email && (
                  <p className="text-sm text-gray-500 mt-1">You'll receive event confirmations and attendee notifications here</p>
                )}
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Phone className="w-4 h-4" />
                  <span>Contact Phone Number *</span>
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={handlePhoneChange}
                  className={`w-full px-4 py-3 border-2 rounded-xl focus:outline-none transition-colors ${
                    phoneError 
                      ? 'border-red-500 focus:border-red-500' 
                      : 'border-gray-200'
                  }`}
                  onFocus={(e) => { if (!phoneError) e.target.style.borderColor = '#27aae2'; }}
                  onBlur={(e) => { 
                    if (formData.phone) validatePhone(formData.phone);
                    if (!phoneError && !formData.phone) e.target.style.borderColor = '';
                  }}
                  placeholder="+254 700 000 000 or 0700 000 000"
                />
                {phoneError && (
                  <p className="text-sm text-red-600 mt-1 flex items-center space-x-1">
                    <span>⚠</span>
                    <span>{phoneError}</span>
                  </p>
                )}
                {!phoneError && formData.phone && (
                  <p className="text-sm text-gray-500 mt-1">This will be displayed to attendees for inquiries</p>
                )}
              </div>

              <div className="flex justify-between pt-4">
                <button
                  onClick={handlePrevious}
                  className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-bold transition-all flex items-center space-x-2"
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#27aae2';
                    e.currentTarget.style.color = '#27aae2';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '';
                    e.currentTarget.style.color = '';
                  }}
                >
                  <ArrowLeft className="w-5 h-5" />
                  <span>Back</span>
                </button>
                <button
                  onClick={handleNext}
                  disabled={!canProceedStep3}
                  className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center space-x-2 ${
                    canProceedStep3
                      ? 'text-white hover:opacity-90'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  style={canProceedStep3 ? { backgroundColor: '#27aae2' } : {}}
                >
                  <span>Next</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Sign Contract */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Partner Agreement</h2>
                <p className="text-gray-600">Review and sign the partner contract</p>
              </div>

              <div className="border-2 rounded-xl p-6" style={{ backgroundColor: '#e6f7ff', borderColor: '#27aae2' }}>
                <h3 className="font-bold text-gray-900 mb-3 flex items-center space-x-2">
                  <FileText className="w-5 h-5" />
                  <span>Partner Terms & Conditions</span>
                </h3>
                <div className="text-sm text-gray-700 space-y-2 mb-4 max-h-60 overflow-y-auto bg-white p-4 rounded-lg">
                  <p className="font-semibold">By signing this agreement, you agree to:</p>
                  <p>• Pay a 7% commission on all ticket sales processed through Niko Free</p>
                  <p>• Ensure all events comply with local laws and regulations</p>
                  <p>• Maintain high quality standards and attendee satisfaction</p>
                  <p>• Provide accurate event information and timely updates</p>
                  <p>• Respond to attendee inquiries within 24 hours</p>
                  <p>• Accept that Niko Free reserves the right to remove events that violate guidelines</p>
                  <p>• Understand that payment processing takes 2-3 business days</p>
                  <p>• Maintain ownership of your event content and data</p>
                  <p>• Comply with our data protection and privacy policies</p>
                  <p className="pt-2 font-semibold">Cancellation & Refund Policy:</p>
                  <p>• Refunds must be processed according to your stated event policy</p>
                  <p>• Partners are responsible for communicating cancellations to attendees</p>
                </div>
                <button 
                  className="text-sm font-medium transition-colors"
                  style={{ color: '#27aae2' }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                >
                  Read Full Terms & Conditions →
                </button>
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <PenTool className="w-4 h-4" />
                  <span>Digital Signature *</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.signature}
                  onChange={(e) => setFormData({ ...formData, signature: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none transition-colors font-cursive text-xl"
                  onFocus={(e) => e.target.style.borderColor = '#27aae2'}
                  onBlur={(e) => { if (!formData.signature) e.target.style.borderColor = ''; }}
                  placeholder="Type your full name as signature"
                  style={{ fontFamily: 'Brush Script MT, cursive', borderColor: formData.signature ? '#27aae2' : '' }}
                />
                <p className="text-sm text-gray-500 mt-1">By typing your name, you agree to sign this contract electronically</p>
              </div>

              <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.acceptTerms}
                    onChange={(e) => setFormData({ ...formData, acceptTerms: e.target.checked })}
                    className="mt-1 w-5 h-5 border-2 border-gray-300 rounded focus:ring-2"
                    style={{ 
                      accentColor: '#27aae2',
                      outlineColor: '#27aae2'
                    }}
                  />
                  <span className="text-sm text-gray-700">
                    I have read and agree to the Partner Terms & Conditions and Privacy Policy. I understand that my digital signature above constitutes a legally binding agreement.
                  </span>
                </label>
              </div>

              <div className="flex justify-between pt-4">
                <button
                  onClick={handlePrevious}
                  className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-bold transition-all flex items-center space-x-2"
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#27aae2';
                    e.currentTarget.style.color = '#27aae2';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '';
                    e.currentTarget.style.color = '';
                  }}
                >
                  <ArrowLeft className="w-5 h-5" />
                  <span>Back</span>
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!canProceedStep4}
                  className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center space-x-2 ${
                    canProceedStep4
                      ? 'text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  style={canProceedStep4 ? { 
                    background: 'linear-gradient(to right, #27aae2, #1a8ec4)'
                  } : {}}
                  onMouseEnter={(e) => {
                    if (canProceedStep4) e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
                  }}
                  onMouseLeave={(e) => {
                    if (canProceedStep4) e.currentTarget.style.boxShadow = '';
                  }}
                >
                  <CheckCircle className="w-5 h-5" />
                  <span>Submit Application</span>
                </button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* <Footer /> */}
      </div>
    </div>
  );
}
