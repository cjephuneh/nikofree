import { useState } from 'react';
import { 
  X, 
  MapPin, 
  Calendar, 
  Tag, 
  Image as ImageIcon, 
  FileText, 
  DollarSign, 
  Users, 
  Link as LinkIcon,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Upload,
  Plus,
  Trash2,
  Check,
  Globe,
  Video
} from 'lucide-react';

interface CreateEventProps {
  isOpen: boolean;
  onClose: () => void;
}

interface EventFormData {
  // Step 1: Location
  locationType: 'physical' | 'online' | 'hybrid';
  locationName: string;
  coordinates: { lat: number; lng: number } | null;
  onlineLink: string;
  linkShareTime: string;
  
  // Step 2: Date & Time
  startDate: string;
  startTime: string;
  endDate: string;
  endTime: string;
  
  // Step 3: Categories
  closedCategories: string[];
  openInterests: string[];
  
  // Step 4: Event Details
  eventName: string;
  eventPhoto: File | null;
  photoPreview: string;
  
  // Step 5: Description & Limits
  description: string;
  attendeeLimit: number | null;
  isUnlimited: boolean;
  
  // Step 6: Pricing
  isFree: boolean;
  ticketTypes: TicketType[];
  
  // Step 7: Hosts & Promo
  hosts: Host[];
  promoCodes: PromoCode[];
}

interface TicketType {
  id: string;
  name: string;
  ticketStructure: 'basic' | 'class' | 'loyalty' | 'season' | 'timeslot';
  // Class-based fields
  classType?: 'vvip' | 'vip' | 'regular';
  // Loyalty-based fields
  loyaltyType?: 'diehard' | 'earlybird' | 'advance' | 'gate';
  // Season-based fields
  seasonType?: 'daily' | 'season';
  seasonDuration?: number; // Number of days for season ticket
  // Timeslot-based fields
  timeslot?: string; // e.g., "9:00 AM - 10:00 AM"
  price: number;
  quantity: number;
  vatIncluded: boolean;
}

interface Host {
  id: string;
  username: string;
  name: string;
  isVerified: boolean;
}

interface PromoCode {
  id: string;
  code: string;
  discount: number;
  discountType: 'percentage' | 'fixed';
  maxUses: number;
  expiryDate: string;
}

const predefinedCategories = [
  'Explore Kenya',
  'Sports & Fitness',
  'Social Activities',
  'Hobbies & Interests',
  'Religious',
  'Autofest',
  'Health & Wellbeing',
  'Music & Dance',
  'Culture',
  'Pets & Animals',
  'Coaching & Support',
  'Business & Networking',
  'Technology',
  'Live Plays',
  'Art & Photography',
  'Shopping',
  'Gaming'
];

export default function CreateEvent({ isOpen, onClose }: CreateEventProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<EventFormData>({
    locationType: 'physical',
    locationName: '',
    coordinates: null,
    onlineLink: '',
    linkShareTime: '',
    startDate: '',
    startTime: '',
    endDate: '',
    endTime: '',
    closedCategories: [],
    openInterests: [],
    eventName: '',
    eventPhoto: null,
    photoPreview: '',
    description: '',
    attendeeLimit: null,
    isUnlimited: true,
    isFree: true,
    ticketTypes: [],
    hosts: [],
    promoCodes: []
  });

  const totalSteps = 7;

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleCategoryToggle = (category: string) => {
    setFormData(prev => ({
      ...prev,
      closedCategories: prev.closedCategories.includes(category)
        ? prev.closedCategories.filter(c => c !== category)
        : [...prev.closedCategories, category]
    }));
  };

  const handleInterestAdd = (interest: string) => {
    if (formData.openInterests.length < 5 && interest.trim() && !formData.openInterests.includes(interest.trim())) {
      setFormData(prev => ({
        ...prev,
        openInterests: [...prev.openInterests, interest.trim()]
      }));
    }
  };

  const handleInterestRemove = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      openInterests: prev.openInterests.filter(i => i !== interest)
    }));
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        eventPhoto: file,
        photoPreview: URL.createObjectURL(file)
      }));
    }
  };

  const generateAIDescription = () => {
    // Simulate AI generation
    const aiDescription = `Join us for an unforgettable experience at ${formData.eventName}! This exciting ${formData.closedCategories.join(', ')} event promises to deliver amazing moments and connections. Whether you're looking to ${formData.openInterests.join(', ')}, this is the perfect opportunity for you. Don't miss out on this incredible gathering!`;
    setFormData(prev => ({ ...prev, description: aiDescription }));
  };

  const addTicketType = () => {
    // Check if trying to add more than 8 timeslot tickets
    const timeslotTickets = formData.ticketTypes.filter(t => t.ticketStructure === 'timeslot');
    if (timeslotTickets.length >= 8) {
      alert('Maximum 8 time slot tickets allowed per event.');
      return;
    }

    const newTicket: TicketType = {
      id: Date.now().toString(),
      name: '',
      ticketStructure: 'basic',
      price: 0,
      quantity: 0,
      vatIncluded: true
    };
    setFormData(prev => ({
      ...prev,
      ticketTypes: [...prev.ticketTypes, newTicket]
    }));
  };

  const removeTicketType = (id: string) => {
    setFormData(prev => ({
      ...prev,
      ticketTypes: prev.ticketTypes.filter(t => t.id !== id)
    }));
  };

  const updateTicketType = (id: string, field: keyof TicketType, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      ticketTypes: prev.ticketTypes.map(t => 
        t.id === id ? { ...t, [field]: value } : t
      )
    }));
  };

  const addPromoCode = () => {
    const newPromo: PromoCode = {
      id: Date.now().toString(),
      code: '',
      discount: 0,
      discountType: 'percentage',
      maxUses: 0,
      expiryDate: ''
    };
    setFormData(prev => ({
      ...prev,
      promoCodes: [...prev.promoCodes, newPromo]
    }));
  };

  const removePromoCode = (id: string) => {
    setFormData(prev => ({
      ...prev,
      promoCodes: prev.promoCodes.filter(p => p.id !== id)
    }));
  };

  const updatePromoCode = (id: string, field: keyof PromoCode, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      promoCodes: prev.promoCodes.map(p => 
        p.id === id ? { ...p, [field]: value } : p
      )
    }));
  };

  const searchHost = (username: string) => {
    // Simulate searching for Niko Free members
    // In production, this would be an API call
    const mockHosts: Host[] = [
      { id: '1', username: '@annalane', name: 'Anna Lane', isVerified: true },
      { id: '2', username: '@victormuli', name: 'Victor Muli', isVerified: true },
      { id: '3', username: '@johndoe', name: 'John Doe', isVerified: false }
    ];
    return mockHosts.filter(h => 
      h.username.toLowerCase().includes(username.toLowerCase()) ||
      h.name.toLowerCase().includes(username.toLowerCase())
    );
  };

  const addHost = (host: Host) => {
    if (formData.hosts.length < 2 && !formData.hosts.find(h => h.id === host.id)) {
      setFormData(prev => ({
        ...prev,
        hosts: [...prev.hosts, host]
      }));
    }
  };

  const removeHost = (id: string) => {
    setFormData(prev => ({
      ...prev,
      hosts: prev.hosts.filter(h => h.id !== id)
    }));
  };

  const handleSubmit = () => {
    // Submit event for approval
    console.log('Event submitted:', formData);
    alert('Event submitted for approval! You will be notified once it\'s approved.');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-[#27aae2] to-[#1e8bb8] px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white">Create New Event</h3>
                <p className="text-sm text-white/80 mt-1">Step {currentStep} of {totalSteps}</p>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Progress bar */}
            <div className="mt-4 bg-white/20 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-white h-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              />
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-6 max-h-[60vh] overflow-y-auto">
            {/* Step 1: Location */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Event Location</h4>
                  
                  {/* Location Type */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, locationType: 'physical' }))}
                      className={`p-4 border-2 rounded-lg transition-all ${
                        formData.locationType === 'physical'
                          ? 'border-[#27aae2] bg-[#27aae2]/10'
                          : 'border-gray-300 dark:border-gray-600 hover:border-[#27aae2]/50'
                      }`}
                    >
                      <MapPin className={`w-8 h-8 mx-auto mb-2 ${
                        formData.locationType === 'physical' ? 'text-[#27aae2]' : 'text-gray-400'
                      }`} />
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Physical</p>
                    </button>

                    <button
                      onClick={() => setFormData(prev => ({ ...prev, locationType: 'online' }))}
                      className={`p-4 border-2 rounded-lg transition-all ${
                        formData.locationType === 'online'
                          ? 'border-[#27aae2] bg-[#27aae2]/10'
                          : 'border-gray-300 dark:border-gray-600 hover:border-[#27aae2]/50'
                      }`}
                    >
                      <Globe className={`w-8 h-8 mx-auto mb-2 ${
                        formData.locationType === 'online' ? 'text-[#27aae2]' : 'text-gray-400'
                      }`} />
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Online</p>
                    </button>

                    <button
                      onClick={() => setFormData(prev => ({ ...prev, locationType: 'hybrid' }))}
                      className={`p-4 border-2 rounded-lg transition-all ${
                        formData.locationType === 'hybrid'
                          ? 'border-[#27aae2] bg-[#27aae2]/10'
                          : 'border-gray-300 dark:border-gray-600 hover:border-[#27aae2]/50'
                      }`}
                    >
                      <Video className={`w-8 h-8 mx-auto mb-2 ${
                        formData.locationType === 'hybrid' ? 'text-[#27aae2]' : 'text-gray-400'
                      }`} />
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Hybrid</p>
                    </button>
                  </div>

                  {/* Physical/Hybrid Location */}
                  {(formData.locationType === 'physical' || formData.locationType === 'hybrid') && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <MapPin className="w-4 h-4 inline mr-1" />
                        Location Name
                      </label>
                      <input
                        type="text"
                        value={formData.locationName}
                        onChange={(e) => setFormData(prev => ({ ...prev, locationName: e.target.value }))}
                        placeholder="e.g., Ngong Hills, Nairobi"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                      />
                      <button className="mt-2 text-sm text-[#27aae2] hover:text-[#1e8bb8] font-medium">
                        📍 Pin on Map
                      </button>
                    </div>
                  )}

                  {/* Online/Hybrid Link */}
                  {(formData.locationType === 'online' || formData.locationType === 'hybrid') && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          <LinkIcon className="w-4 h-4 inline mr-1" />
                          Event Link
                        </label>
                        <input
                          type="url"
                          value={formData.onlineLink}
                          onChange={(e) => setFormData(prev => ({ ...prev, onlineLink: e.target.value }))}
                          placeholder="https://zoom.us/j/..."
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Link Share Time
                        </label>
                        <select
                          value={formData.linkShareTime}
                          onChange={(e) => setFormData(prev => ({ ...prev, linkShareTime: e.target.value }))}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                        >
                          <option value="">Select when to share link</option>
                          <option value="immediately">Immediately after booking</option>
                          <option value="1hour">1 hour before event</option>
                          <option value="30min">30 minutes before event</option>
                          <option value="15min">15 minutes before event</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Step 2: Date & Time */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <Calendar className="w-5 h-5 inline mr-2" />
                    Date & Time
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Start Date
                      </label>
                      <input
                        type="date"
                        value={formData.startDate}
                        onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Start Time
                      </label>
                      <input
                        type="time"
                        value={formData.startTime}
                        onChange={(e) => setFormData(prev => ({ ...prev, startTime: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        End Date
                      </label>
                      <input
                        type="date"
                        value={formData.endDate}
                        onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        End Time
                      </label>
                      <input
                        type="time"
                        value={formData.endTime}
                        onChange={(e) => setFormData(prev => ({ ...prev, endTime: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Categories */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <Tag className="w-5 h-5 inline mr-2" />
                    Categories & Interests
                  </h4>

                  {/* Closed Categories */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Select Categories (Multiple Choice)
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {predefinedCategories.map(category => (
                        <button
                          key={category}
                          onClick={() => handleCategoryToggle(category)}
                          className={`px-4 py-2 rounded-lg border-2 transition-all text-sm font-medium ${
                            formData.closedCategories.includes(category)
                              ? 'border-[#27aae2] bg-[#27aae2] text-white'
                              : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-[#27aae2]'
                          }`}
                        >
                          {formData.closedCategories.includes(category) && (
                            <Check className="w-4 h-4 inline mr-1" />
                          )}
                          {category}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Open Interests */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Add Custom Interests (Max 5)
                    </label>
                    <div className="flex gap-2 mb-3">
                      <input
                        type="text"
                        id="interestInput"
                        placeholder="e.g., Hiking, Photography"
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleInterestAdd((e.target as HTMLInputElement).value);
                            (e.target as HTMLInputElement).value = '';
                          }
                        }}
                      />
                      <button
                        onClick={() => {
                          const input = document.getElementById('interestInput') as HTMLInputElement;
                          handleInterestAdd(input.value);
                          input.value = '';
                        }}
                        disabled={formData.openInterests.length >= 5}
                        className="px-4 py-2 bg-[#27aae2] text-white rounded-lg hover:bg-[#1e8bb8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        <Plus className="w-5 h-5" />
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {formData.openInterests.map(interest => (
                        <span
                          key={interest}
                          className="px-3 py-1 bg-[#27aae2]/10 text-[#27aae2] rounded-full text-sm font-medium flex items-center gap-2"
                        >
                          {interest}
                          <button
                            onClick={() => handleInterestRemove(interest)}
                            className="hover:text-red-500"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      {formData.openInterests.length}/5 interests added
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Event Name & Photo */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Event Details
                  </h4>

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Event Name
                    </label>
                    <input
                      type="text"
                      value={formData.eventName}
                      onChange={(e) => setFormData(prev => ({ ...prev, eventName: e.target.value }))}
                      placeholder="e.g., PICNICS AT NGONG HILLS"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <ImageIcon className="w-4 h-4 inline mr-1" />
                      Event Photo
                    </label>
                    
                    {formData.photoPreview ? (
                      <div className="relative">
                        <img
                          src={formData.photoPreview}
                          alt="Event preview"
                          className="w-full h-64 object-cover rounded-lg"
                        />
                        <button
                          onClick={() => setFormData(prev => ({ ...prev, eventPhoto: null, photoPreview: '' }))}
                          className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-[#27aae2] transition-colors">
                        <Upload className="w-12 h-12 text-gray-400 mb-2" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">Click to upload event photo</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">PNG, JPG up to 10MB</p>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handlePhotoUpload}
                          className="hidden"
                        />
                      </label>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 5: Description & Limits */}
            {currentStep === 5 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <FileText className="w-5 h-5 inline mr-2" />
                    Description & Capacity
                  </h4>

                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Event Description
                      </label>
                      <button
                        onClick={generateAIDescription}
                        className="flex items-center gap-1 px-3 py-1 text-sm bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all"
                      >
                        <Sparkles className="w-4 h-4" />
                        AI Generate
                      </button>
                    </div>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      rows={6}
                      placeholder="Describe your event..."
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      <Users className="w-4 h-4 inline mr-1" />
                      Attendee Capacity
                    </label>
                    
                    <div className="flex items-center gap-4 mb-4">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          checked={formData.isUnlimited}
                          onChange={() => setFormData(prev => ({ ...prev, isUnlimited: true, attendeeLimit: null }))}
                          className="w-4 h-4 text-[#27aae2] focus:ring-[#27aae2]"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Unlimited</span>
                      </label>
                      
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          checked={!formData.isUnlimited}
                          onChange={() => setFormData(prev => ({ ...prev, isUnlimited: false }))}
                          className="w-4 h-4 text-[#27aae2] focus:ring-[#27aae2]"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Limited</span>
                      </label>
                    </div>

                    {!formData.isUnlimited && (
                      <input
                        type="number"
                        value={formData.attendeeLimit || ''}
                        onChange={(e) => setFormData(prev => ({ ...prev, attendeeLimit: parseInt(e.target.value) || null }))}
                        placeholder="Maximum attendees"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                      />
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 6: Pricing */}
            {currentStep === 6 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <DollarSign className="w-5 h-5 inline mr-2" />
                    Event Pricing
                  </h4>

                  <div className="flex items-center gap-4 mb-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={formData.isFree}
                        onChange={() => setFormData(prev => ({ ...prev, isFree: true, ticketTypes: [] }))}
                        className="w-4 h-4 text-[#27aae2] focus:ring-[#27aae2]"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Free Event</span>
                    </label>
                    
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={!formData.isFree}
                        onChange={() => setFormData(prev => ({ ...prev, isFree: false }))}
                        className="w-4 h-4 text-[#27aae2] focus:ring-[#27aae2]"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Paid Event</span>
                    </label>
                  </div>

                  {!formData.isFree && (
                    <div>
                      {/* Ticket Types Info */}
                      <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                        <h5 className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">Ticket Types Guide:</h5>
                        <ul className="text-xs text-blue-800 dark:text-blue-400 space-y-1">
                          <li><strong>Basic:</strong> One uniform price for all attendees (e.g., Tour packages)</li>
                          <li><strong>Class-Based:</strong> Different pricing tiers - VVIP, VIP, Regular</li>
                          <li><strong>Loyalty:</strong> Reward early/loyal customers - Die Hard, Early Bird, Advance, Gate</li>
                          <li><strong>Season:</strong> Daily tickets or multi-day passes for events spanning multiple days</li>
                          <li><strong>Time Slot:</strong> Book specific time periods (max 8 slots, e.g., hourly training sessions)</li>
                        </ul>
                      </div>

                      <div className="flex items-center justify-between mb-4">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Ticket Types
                        </label>
                        <button
                          onClick={addTicketType}
                          className="flex items-center gap-1 px-3 py-1 bg-[#27aae2] text-white rounded-lg hover:bg-[#1e8bb8] transition-colors text-sm"
                        >
                          <Plus className="w-4 h-4" />
                          Add Ticket
                        </button>
                      </div>

                      <div className="space-y-4">
                        {formData.ticketTypes.map((ticket) => (
                          <div key={ticket.id} className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg">
                            <div className="space-y-4">
                              {/* Ticket Structure Selection */}
                              <div>
                                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Ticket Structure</label>
                                <select
                                  value={ticket.ticketStructure}
                                  onChange={(e) => updateTicketType(ticket.id, 'ticketStructure', e.target.value)}
                                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                >
                                  <option value="basic">Basic Ticket (Uniform Price)</option>
                                  <option value="class">Class-Based (VVIP, VIP, Regular)</option>
                                  <option value="loyalty">Loyalty-Based (Die Hard, Early Bird, etc.)</option>
                                  <option value="season">Season Ticket (Daily/Multi-day)</option>
                                  <option value="timeslot">Time Slot Ticket</option>
                                </select>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Ticket Name */}
                                <div>
                                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Ticket Name</label>
                                  <input
                                    type="text"
                                    value={ticket.name}
                                    onChange={(e) => updateTicketType(ticket.id, 'name', e.target.value)}
                                    placeholder={
                                      ticket.ticketStructure === 'basic' ? 'e.g., General Admission' :
                                      ticket.ticketStructure === 'class' ? 'e.g., VIP Access' :
                                      ticket.ticketStructure === 'loyalty' ? 'e.g., Early Bird Special' :
                                      ticket.ticketStructure === 'season' ? 'e.g., 3-Day Pass' :
                                      'e.g., Morning Session'
                                    }
                                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                  />
                                </div>

                                {/* Class Type (only for class-based) */}
                                {ticket.ticketStructure === 'class' && (
                                  <div>
                                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Class Type</label>
                                    <select
                                      value={ticket.classType || 'regular'}
                                      onChange={(e) => updateTicketType(ticket.id, 'classType', e.target.value)}
                                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                    >
                                      <option value="vvip">VVIP</option>
                                      <option value="vip">VIP</option>
                                      <option value="regular">Regular</option>
                                    </select>
                                  </div>
                                )}

                                {/* Loyalty Type (only for loyalty-based) */}
                                {ticket.ticketStructure === 'loyalty' && (
                                  <div>
                                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Loyalty Type</label>
                                    <select
                                      value={ticket.loyaltyType || 'earlybird'}
                                      onChange={(e) => updateTicketType(ticket.id, 'loyaltyType', e.target.value)}
                                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                    >
                                      <option value="diehard">Die Hard</option>
                                      <option value="earlybird">Early Bird</option>
                                      <option value="advance">Advance</option>
                                      <option value="gate">Gate Ticket</option>
                                    </select>
                                  </div>
                                )}

                                {/* Season Type (only for season-based) */}
                                {ticket.ticketStructure === 'season' && (
                                  <>
                                    <div>
                                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Season Type</label>
                                      <select
                                        value={ticket.seasonType || 'daily'}
                                        onChange={(e) => updateTicketType(ticket.id, 'seasonType', e.target.value)}
                                        className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                      >
                                        <option value="daily">Daily Ticket</option>
                                        <option value="season">Season Ticket</option>
                                      </select>
                                    </div>
                                    {ticket.seasonType === 'season' && (
                                      <div>
                                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Duration (Days)</label>
                                        <input
                                          type="number"
                                          value={ticket.seasonDuration || ''}
                                          onChange={(e) => updateTicketType(ticket.id, 'seasonDuration', parseInt(e.target.value) || 1)}
                                          placeholder="e.g., 3"
                                          min="1"
                                          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                        />
                                      </div>
                                    )}
                                  </>
                                )}

                                {/* Time Slot (only for timeslot-based) */}
                                {ticket.ticketStructure === 'timeslot' && (
                                  <div>
                                    <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Time Slot</label>
                                    <input
                                      type="text"
                                      value={ticket.timeslot || ''}
                                      onChange={(e) => updateTicketType(ticket.id, 'timeslot', e.target.value)}
                                      placeholder="e.g., 9:00 AM - 10:00 AM"
                                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                    />
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Max 8 time slots per event</p>
                                  </div>
                                )}

                                {/* Price */}
                                <div>
                                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Price (KES)</label>
                                  <input
                                    type="number"
                                    value={ticket.price || ''}
                                    onChange={(e) => updateTicketType(ticket.id, 'price', parseFloat(e.target.value) || 0)}
                                    placeholder="0"
                                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                  />
                                </div>

                                {/* Quantity */}
                                <div>
                                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Quantity Available</label>
                                  <input
                                    type="number"
                                    value={ticket.quantity || ''}
                                    onChange={(e) => updateTicketType(ticket.id, 'quantity', parseInt(e.target.value) || 0)}
                                    placeholder="0"
                                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                                  />
                                </div>
                              </div>

                              {/* VAT and Delete */}
                              <div className="flex items-center justify-between pt-2">
                                <label className="flex items-center gap-2 cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={ticket.vatIncluded}
                                    onChange={(e) => updateTicketType(ticket.id, 'vatIncluded', e.target.checked)}
                                    className="w-4 h-4 text-[#27aae2] rounded focus:ring-[#27aae2]"
                                  />
                                  <span className="text-xs text-gray-700 dark:text-gray-300">VAT Included</span>
                                </label>

                                <button
                                  onClick={() => removeTicketType(ticket.id)}
                                  className="flex items-center gap-1 px-3 py-1.5 text-red-500 border border-red-300 dark:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-xs"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                  Remove
                                </button>
                              </div>

                              {/* Ticket Preview */}
                              <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Preview:</p>
                                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                                  {ticket.name || 'Ticket Name'} 
                                  {ticket.ticketStructure === 'class' && ` (${ticket.classType?.toUpperCase() || 'CLASS'})`}
                                  {ticket.ticketStructure === 'loyalty' && ` (${ticket.loyaltyType?.replace(/([A-Z])/g, ' $1').trim() || 'LOYALTY TYPE'})`}
                                  {ticket.ticketStructure === 'season' && ticket.seasonType === 'season' && ` (${ticket.seasonDuration || 0}-Day Pass)`}
                                  {ticket.ticketStructure === 'timeslot' && ` (${ticket.timeslot || 'TIME SLOT'})`}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  KES {ticket.price.toLocaleString()} {ticket.vatIncluded && '(incl. VAT)'} • {ticket.quantity} available
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}

                        {formData.ticketTypes.length === 0 && (
                          <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                            No ticket types added yet. Click "Add Ticket" to create one.
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Step 7: Hosts & Promo Codes */}
            {currentStep === 7 && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    <Users className="w-5 h-5 inline mr-2" />
                    Hosts & Promotions
                  </h4>

                  {/* Hosts Section */}
                  <div className="mb-8">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Add Event Hosts (Max 2)
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                      Hosts must be Niko Free members and will receive all RSVPs, bookings, and bucket lists.
                    </p>

                    {formData.hosts.length < 2 && (
                      <div className="mb-4">
                        <input
                          type="text"
                          placeholder="Search by username or name..."
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                          onChange={(e) => {
                            // In production, this would trigger a search
                            if (e.target.value) {
                              const results = searchHost(e.target.value);
                              // Show results dropdown (simplified for demo)
                              console.log('Search results:', results);
                            }
                          }}
                        />
                        {/* Demo: Add some sample hosts */}
                        <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Suggested hosts:</p>
                          <div className="space-y-2">
                            <button
                              onClick={() => addHost({ id: '1', username: '@annalane', name: 'Anna Lane', isVerified: true })}
                              className="w-full flex items-center justify-between px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-[#27aae2] transition-colors"
                            >
                              <div className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-[#27aae2] to-[#1e8bb8] rounded-full flex items-center justify-center text-white text-sm font-bold">
                                  AL
                                </div>
                                <div className="text-left">
                                  <p className="text-sm font-medium text-gray-900 dark:text-white">Anna Lane</p>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">@annalane</p>
                                </div>
                              </div>
                              {formData.hosts.find(h => h.id === '1') ? (
                                <Check className="w-5 h-5 text-green-500" />
                              ) : (
                                <Plus className="w-5 h-5 text-[#27aae2]" />
                              )}
                            </button>

                            <button
                              onClick={() => addHost({ id: '2', username: '@victormuli', name: 'Victor Muli', isVerified: true })}
                              className="w-full flex items-center justify-between px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-[#27aae2] transition-colors"
                            >
                              <div className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                                  VM
                                </div>
                                <div className="text-left">
                                  <p className="text-sm font-medium text-gray-900 dark:text-white">Victor Muli</p>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">@victormuli</p>
                                </div>
                              </div>
                              {formData.hosts.find(h => h.id === '2') ? (
                                <Check className="w-5 h-5 text-green-500" />
                              ) : (
                                <Plus className="w-5 h-5 text-[#27aae2]" />
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Selected Hosts */}
                    {formData.hosts.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-gray-700 dark:text-gray-300">Selected Hosts:</p>
                        {formData.hosts.map(host => (
                          <div key={host.id} className="flex items-center justify-between px-4 py-3 bg-[#27aae2]/10 border border-[#27aae2]/30 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-gradient-to-br from-[#27aae2] to-[#1e8bb8] rounded-full flex items-center justify-center text-white font-bold">
                                {host.name.split(' ').map(n => n[0]).join('')}
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">{host.name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">{host.username}</p>
                              </div>
                            </div>
                            <button
                              onClick={() => removeHost(host.id)}
                              className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Host Preview */}
                    {formData.hosts.length > 0 && (
                      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                        <p className="text-xs text-blue-600 dark:text-blue-400 mb-2">Event will display as:</p>
                        <p className="font-bold text-gray-900 dark:text-white">{formData.eventName || 'EVENT NAME'}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Hosted by {formData.hosts.map(h => h.name).join(' & ')}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Promo Codes Section */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Promo Codes (Optional)
                      </label>
                      <button
                        onClick={addPromoCode}
                        className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                      >
                        <Plus className="w-4 h-4" />
                        Add Promo
                      </button>
                    </div>

                    <div className="space-y-3">
                      {formData.promoCodes.map(promo => (
                        <div key={promo.id} className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Promo Code</label>
                              <input
                                type="text"
                                value={promo.code}
                                onChange={(e) => updatePromoCode(promo.id, 'code', e.target.value.toUpperCase())}
                                placeholder="e.g., EARLYBIRD"
                                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                              />
                            </div>

                            <div>
                              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Discount Type</label>
                              <select
                                value={promo.discountType}
                                onChange={(e) => updatePromoCode(promo.id, 'discountType', e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                              >
                                <option value="percentage">Percentage (%)</option>
                                <option value="fixed">Fixed Amount (KES)</option>
                              </select>
                            </div>

                            <div>
                              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Discount Value</label>
                              <input
                                type="number"
                                value={promo.discount}
                                onChange={(e) => updatePromoCode(promo.id, 'discount', parseFloat(e.target.value) || 0)}
                                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                              />
                            </div>

                            <div>
                              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Max Uses</label>
                              <input
                                type="number"
                                value={promo.maxUses}
                                onChange={(e) => updatePromoCode(promo.id, 'maxUses', parseInt(e.target.value) || 0)}
                                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                              />
                            </div>

                            <div>
                              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Expiry Date</label>
                              <input
                                type="date"
                                value={promo.expiryDate}
                                onChange={(e) => updatePromoCode(promo.id, 'expiryDate', e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#27aae2]"
                              />
                            </div>

                            <div className="flex items-end">
                              <button
                                onClick={() => removePromoCode(promo.id)}
                                className="w-full p-2 text-red-500 border border-red-300 dark:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                              >
                                <Trash2 className="w-4 h-4 mx-auto" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}

                      {formData.promoCodes.length === 0 && (
                        <p className="text-center text-gray-500 dark:text-gray-400 py-4 text-sm">
                          No promo codes added. Promo codes are optional.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex items-center justify-between">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-5 h-5" />
              Back
            </button>

            <div className="flex items-center gap-2">
              {currentStep < totalSteps ? (
                <button
                  onClick={handleNext}
                  className="flex items-center gap-2 px-6 py-2 bg-[#27aae2] text-white rounded-lg hover:bg-[#1e8bb8] transition-colors"
                >
                  Next
                  <ChevronRight className="w-5 h-5" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  className="flex items-center gap-2 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <Check className="w-5 h-5" />
                  Submit for Approval
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
