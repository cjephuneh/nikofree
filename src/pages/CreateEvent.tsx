import { MapPin, Calendar, Clock, Upload, Tag, Users, DollarSign, Sparkles, Plus, X } from 'lucide-react';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface CreateEventProps {
  onNavigate: (page: string) => void;
}

export default function CreateEvent({ onNavigate }: CreateEventProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
    time: '',
    location: '',
    category: '',
    interests: [] as string[],
    ticketType: 'free',
    price: '',
    totalTickets: '',
    useAI: false
  });

  const [currentInterest, setCurrentInterest] = useState('');

  const handleAddInterest = () => {
    if (currentInterest && formData.interests.length < 5) {
      setFormData({
        ...formData,
        interests: [...formData.interests, currentInterest]
      });
      setCurrentInterest('');
    }
  };

  const handleRemoveInterest = (index: number) => {
    setFormData({
      ...formData,
      interests: formData.interests.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNavigate('partner-dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onNavigate={onNavigate} />

      <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <button
            onClick={() => onNavigate('partner-dashboard')}
            className="text-blue-100 hover:text-white mb-6 flex items-center space-x-2 transition-colors"
          >
            <span>←</span>
            <span>Back to Dashboard</span>
          </button>
          <h1 className="text-5xl font-bold text-white mb-4">Create New Event</h1>
          <p className="text-xl text-blue-100">Fill in the details to create your amazing event</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 pb-20">
        <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div>
              <label className="text-sm font-semibold text-gray-700 mb-2 block">
                Event Title
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors text-lg"
                placeholder="Give your event an exciting title"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-semibold text-gray-700">
                  Event Description
                </label>
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, useAI: !formData.useAI })}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    formData.useAI
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Sparkles className="w-4 h-4" />
                  <span>AI Assist</span>
                </button>
              </div>
              <textarea
                required
                rows={6}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors resize-none"
                placeholder="Describe what makes your event special and what attendees can expect"
              />
              {formData.useAI && (
                <p className="text-sm text-purple-600 mt-2 flex items-center space-x-1">
                  <Sparkles className="w-4 h-4" />
                  <span>AI will help enhance your description</span>
                </p>
              )}
            </div>

            <div>
              <label className="text-sm font-semibold text-gray-700 mb-2 block">
                Event Photo
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-500 transition-colors cursor-pointer bg-gray-50">
                <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2 font-medium">Click to upload event photo</p>
                <p className="text-sm text-gray-500">PNG, JPG up to 10MB • Recommended: 1200x800px</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Calendar className="w-4 h-4" />
                  <span>Event Date</span>
                </label>
                <input
                  type="date"
                  required
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                  <Clock className="w-4 h-4" />
                  <span>Event Time</span>
                </label>
                <input
                  type="time"
                  required
                  value={formData.time}
                  onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <MapPin className="w-4 h-4" />
                <span>Location</span>
              </label>
              <input
                type="text"
                required
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Venue name or online meeting link"
              />
              <div className="mt-3 h-48 bg-gray-100 rounded-xl flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <MapPin className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm">Map pin location selector</p>
                </div>
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <Tag className="w-4 h-4" />
                <span>Category</span>
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
              <label className="text-sm font-semibold text-gray-700 mb-2 block">
                Interests & Tags (max 5)
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentInterest}
                  onChange={(e) => setCurrentInterest(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddInterest())}
                  className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="Add interests like 'AI', 'Networking', 'Startups'"
                  disabled={formData.interests.length >= 5}
                />
                <button
                  type="button"
                  onClick={handleAddInterest}
                  disabled={formData.interests.length >= 5 || !currentInterest}
                  className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Plus className="w-5 h-5" />
                  <span>Add</span>
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.interests.map((interest, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium flex items-center space-x-2"
                  >
                    <span>{interest}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveInterest(index)}
                      className="hover:text-blue-900"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div className="border-t-2 border-gray-200 pt-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Ticket Information</h3>

              <div className="mb-6">
                <label className="text-sm font-semibold text-gray-700 mb-3 block">
                  Ticket Type
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, ticketType: 'free' })}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.ticketType === 'free'
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-bold text-gray-900 mb-1">Free Event</div>
                    <div className="text-sm text-gray-600">No charge for attendees</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, ticketType: 'paid' })}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.ticketType === 'paid'
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-bold text-gray-900 mb-1">Paid Event</div>
                    <div className="text-sm text-gray-600">Set ticket price</div>
                  </button>
                </div>
              </div>

              {formData.ticketType === 'paid' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                      <DollarSign className="w-4 h-4" />
                      <span>Ticket Price (KES)</span>
                    </label>
                    <input
                      type="number"
                      required={formData.ticketType === 'paid'}
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                      placeholder="1000"
                    />
                    <p className="text-xs text-gray-500 mt-1">7% platform commission applies</p>
                  </div>

                  <div>
                    <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                      <Users className="w-4 h-4" />
                      <span>Total Tickets Available</span>
                    </label>
                    <input
                      type="number"
                      required={formData.ticketType === 'paid'}
                      value={formData.totalTickets}
                      onChange={(e) => setFormData({ ...formData, totalTickets: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                      placeholder="100"
                    />
                  </div>
                </div>
              )}

              {formData.ticketType === 'free' && (
                <div>
                  <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                    <Users className="w-4 h-4" />
                    <span>Expected Attendees</span>
                  </label>
                  <input
                    type="number"
                    value={formData.totalTickets}
                    onChange={(e) => setFormData({ ...formData, totalTickets: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                    placeholder="100"
                  />
                </div>
              )}
            </div>

            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
              <h4 className="font-bold text-gray-900 mb-2">Review Before Submitting</h4>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• Your event will be reviewed by our team within 24 hours</li>
                <li>• Ensure all information is accurate and complete</li>
                <li>• You can edit your event after approval</li>
                <li>• {formData.ticketType === 'paid' ? '7% commission applies to all ticket sales' : 'Free events have no commission'}</li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                type="button"
                onClick={() => onNavigate('partner-dashboard')}
                className="flex-1 px-8 py-4 border-2 border-gray-200 text-gray-700 rounded-xl font-bold hover:border-blue-500 hover:text-blue-600 transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-bold hover:shadow-xl transform hover:scale-105 transition-all"
              >
                Submit for Approval
              </button>
            </div>
          </form>
        </div>
      </div>

      <Footer />
    </div>
  );
}
