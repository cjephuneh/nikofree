import { Calendar, MapPin, Users, Share2, Heart, Download, Clock, Tag, ExternalLink, ChevronLeft } from 'lucide-react';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import LoginModal from '../components/LoginModal';
import SignupModal from '../components/SignupModal';

interface EventDetailPageProps {
  eventId: string;
  onNavigate: (page: string) => void;
}

export default function EventDetailPage({ onNavigate }: EventDetailPageProps) {
  const [isRSVPed, setIsRSVPed] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);

  const event = {
    title: 'Nairobi Tech Summit 2025',
    image: 'https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg?auto=compress&cs=tinysrgb&w=1200',
    description: 'Join us for the biggest tech summit in East Africa! Connect with industry leaders, innovative startups, and tech enthusiasts. Experience keynote speeches, panel discussions, networking sessions, and hands-on workshops covering AI, blockchain, cloud computing, and more. This is your opportunity to shape the future of technology in Africa.',
    fullDescription: `The Nairobi Tech Summit 2025 brings together the brightest minds in technology for three days of innovation, learning, and networking.

What to Expect:
• Keynote speeches from global tech leaders
• Interactive workshops on emerging technologies
• Startup pitch competitions with prizes
• Networking sessions with investors and industry experts
• Exhibition hall featuring the latest tech innovations
• Panel discussions on Africa's digital future

Who Should Attend:
• Software developers and engineers
• Entrepreneurs and startup founders
• Technology students and researchers
• Investors and venture capitalists
• Anyone passionate about technology and innovation

Don't miss this opportunity to be part of Africa's tech revolution!`,
    date: 'Saturday, November 2, 2025',
    time: '9:00 AM - 6:00 PM',
    location: 'Kenyatta International Convention Centre, Nairobi',
    category: 'Technology',
    interests: ['AI & Machine Learning', 'Blockchain', 'Cloud Computing', 'Startups', 'Innovation'],
    attendees: 847,
    price: 'KES 2,500',
    isFree: false,
    host: {
      name: 'Tech Hub Africa',
      avatar: 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=100',
      role: 'Technology Community'
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onNavigate={onNavigate} />

      <button
        onClick={() => onNavigate('landing')}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors"
      >
        <ChevronLeft className="w-5 h-5" />
        <span className="font-medium">Back to Events</span>
      </button>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl overflow-hidden shadow-lg">
              <div className="relative h-96">
                <img
                  src={event.image}
                  alt={event.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-4 left-4">
                  <span className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-full">
                    {event.category}
                  </span>
                </div>
              </div>

              <div className="p-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-6">{event.title}</h1>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Calendar className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Date</p>
                      <p className="font-semibold text-gray-900">{event.date}</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Clock className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Time</p>
                      <p className="font-semibold text-gray-900">{event.time}</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <MapPin className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Location</p>
                      <p className="font-semibold text-gray-900">{event.location}</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Attendees</p>
                      <div className="flex items-center space-x-2">
                        <div className="flex -space-x-2">
                          <img
                            src="https://i.pravatar.cc/150?img=15"
                            alt="Attendee"
                            className="w-8 h-8 rounded-full border-2 border-white"
                          />
                          <img
                            src="https://i.pravatar.cc/150?img=22"
                            alt="Attendee"
                            className="w-8 h-8 rounded-full border-2 border-white"
                          />
                          <img
                            src="https://i.pravatar.cc/150?img=35"
                            alt="Attendee"
                            className="w-8 h-8 rounded-full border-2 border-white"
                          />
                        </div>
                        <button
                          onClick={() => setShowLoginModal(true)}
                          className="text-blue-600 hover:text-blue-700 font-semibold text-sm transition-colors"
                        >
                          See All
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">About This Event</h2>
                  <p className="text-gray-700 leading-relaxed mb-4">{event.description}</p>
                  <div className="prose prose-lg max-w-none text-gray-700 whitespace-pre-line">
                    {event.fullDescription}
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-8 mt-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Interests & Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {event.interests.map((interest, index) => (
                      <span
                        key={index}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm font-medium hover:bg-blue-50 hover:text-blue-600 transition-colors cursor-pointer"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-8 mt-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Hosted By</h3>
                  <div className="flex items-center space-x-4">
                    <img
                      src={event.host.avatar}
                      alt={event.host.name}
                      className="w-16 h-16 rounded-full object-cover"
                    />
                    <div>
                      <h4 className="font-semibold text-gray-900 text-lg">{event.host.name}</h4>
                      <p className="text-gray-600">{event.host.role}</p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-8 mt-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Reviews</h3>
                  <div className="space-y-6">
                    <div className="flex items-start space-x-4">
                      <img
                        src="https://i.pravatar.cc/150?img=12"
                        alt="Reviewer"
                        className="w-12 h-12 rounded-full object-cover flex-shrink-0"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-900">Sarah Johnson</h4>
                            <p className="text-sm text-gray-600">2 weeks ago</p>
                          </div>
                          <div className="flex items-center space-x-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <svg key={star} className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 20 20">
                                <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                              </svg>
                            ))}
                          </div>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                          Amazing event! The speakers were incredibly insightful and the networking opportunities were fantastic. Learned so much about AI and blockchain applications in Africa.
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-4">
                      <img
                        src="https://i.pravatar.cc/150?img=33"
                        alt="Reviewer"
                        className="w-12 h-12 rounded-full object-cover flex-shrink-0"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-900">Michael Omondi</h4>
                            <p className="text-sm text-gray-600">1 month ago</p>
                          </div>
                          <div className="flex items-center space-x-1">
                            {[1, 2, 3, 4].map((star) => (
                              <svg key={star} className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 20 20">
                                <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                              </svg>
                            ))}
                            <svg className="w-5 h-5 text-gray-300 fill-current" viewBox="0 0 20 20">
                              <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                            </svg>
                          </div>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                          Great summit with lots of valuable content. The venue was perfect and well-organized. Would have loved more hands-on workshop time though.
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-4">
                      <img
                        src="https://i.pravatar.cc/150?img=27"
                        alt="Reviewer"
                        className="w-12 h-12 rounded-full object-cover flex-shrink-0"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-900">Amina Hassan</h4>
                            <p className="text-sm text-gray-600">3 weeks ago</p>
                          </div>
                          <div className="flex items-center space-x-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <svg key={star} className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 20 20">
                                <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                              </svg>
                            ))}
                          </div>
                        </div>
                        <p className="text-gray-700 leading-relaxed">
                          Exceeded my expectations! Made valuable connections with investors and fellow entrepreneurs. The pitch competition was particularly inspiring. Definitely attending next year!
                        </p>
                      </div>
                    </div>

                    <button className="w-full py-3 border-2 border-gray-200 rounded-xl font-semibold text-gray-700 hover:border-blue-500 hover:text-blue-600 transition-all">
                      Load More Reviews
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-4">
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <div className="mb-6">
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-3xl font-bold text-gray-900">{event.price}</span>
                    <span className="text-sm text-gray-600">per ticket</span>
                  </div>
                  <p className="text-sm text-gray-600">Includes all summit activities</p>
                </div>

                <button
                  onClick={() => setIsRSVPed(!isRSVPed)}
                  className={`w-full py-4 rounded-xl font-bold text-lg transition-all transform hover:scale-105 ${
                    isRSVPed
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-xl'
                  }`}
                >
                  {isRSVPed ? 'Ticket Purchased!' : 'Buy Ticket'}
                </button>

                <div className="grid grid-cols-3 gap-2 mt-4">
                  <button
                    onClick={() => setIsFavorited(!isFavorited)}
                    className={`py-3 rounded-xl border-2 transition-all flex items-center justify-center ${
                      isFavorited
                        ? 'border-red-500 bg-red-50 text-red-500'
                        : 'border-gray-200 hover:border-red-500 hover:text-red-500'
                    }`}
                  >
                    <Heart className={`w-5 h-5 ${isFavorited ? 'fill-red-500' : ''}`} />
                  </button>
                  <button className="py-3 rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:text-blue-500 transition-all flex items-center justify-center">
                    <Share2 className="w-5 h-5" />
                  </button>
                  <button className="py-3 rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:text-blue-500 transition-all flex items-center justify-center">
                    <Download className="w-5 h-5" />
                  </button>
                </div>

                <div className="mt-6 space-y-3">
                  <button className="w-full py-3 border-2 border-gray-200 rounded-xl font-semibold text-gray-700 hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center space-x-2">
                    <Calendar className="w-5 h-5" />
                    <span>Add to Calendar</span>
                  </button>
                  <button className="w-full py-3 border-2 border-gray-200 rounded-xl font-semibold text-gray-700 hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center space-x-2">
                    <ExternalLink className="w-5 h-5" />
                    <span>View on Map</span>
                  </button>
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6">
                <div className="flex items-start space-x-3 mb-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Tag className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 mb-1">Special Offer</h3>
                    <p className="text-sm text-gray-700">Use code EARLY25 for 20% off</p>
                  </div>
                </div>
                <p className="text-xs text-gray-600">Valid for the first 100 tickets only</p>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="font-bold text-gray-900 mb-4">Share Event</h3>
                <div className="space-y-2">
                  <button className="w-full py-2.5 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm">
                    Share on WhatsApp
                  </button>
                  <button className="w-full py-2.5 px-4 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors text-sm">
                    Share on LinkedIn
                  </button>
                  <button className="w-full py-2.5 px-4 border-2 border-gray-200 text-gray-700 rounded-lg font-medium hover:border-gray-300 transition-colors text-sm">
                    Copy Link
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />

      {/* Login Modal */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onNavigate={onNavigate}
        onSwitchToSignup={() => {
          setShowLoginModal(false);
          setShowSignupModal(true);
        }}
      />

      {/* Signup Modal */}
      <SignupModal
        onClose={() => setShowSignupModal(false)}
        onSignup={() => {
          setIsLoggedIn(true);
          setShowSignupModal(false);
        }}
        onSwitchToLogin={() => {
          setShowSignupModal(false);
          setShowLoginModal(true);
        }}
      />
    </div>
  );
}
