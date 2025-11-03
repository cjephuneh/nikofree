import React, { useState } from 'react';
import { Search, MapPin, ChevronLeft, ChevronRight, Plane, Dumbbell, Users, Music, Heart, Dog, Car, Sparkles, Brain, Gamepad2, ShoppingBag, Church, Target, Camera, Calendar, Share2 } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';

interface LandingPageProps {
  onNavigate: (page: string) => void;
  onEventClick: (eventId: string) => void;
}

export default function LandingPage({ onNavigate, onEventClick }: LandingPageProps) {
  const [currentBanner, setCurrentBanner] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('Detecting location...');
  const [locationPlaceholder, setLocationPlaceholder] = useState('Detecting location...');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const categoriesRef = React.useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [locationSuggestions, setLocationSuggestions] = useState<Array<{display_name: string, lat: string, lon: string}>>([]);
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false);
  const locationInputRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    // Get user's location on component mount
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          
          // Use reverse geocoding to get location name
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
            );
            const data = await response.json();
            const city = data.address.city || data.address.town || data.address.county || data.address.state;
            const country = data.address.country;
            const locationString = `${city}, ${country}`;
            setSelectedLocation(locationString);
            setLocationPlaceholder(locationString);
          } catch (error) {
            console.error('Error getting location name:', error);
            setSelectedLocation('Nairobi, Kenya');
            setLocationPlaceholder('Nairobi, Kenya');
          }
        },
        (error) => {
          console.error('Error getting location:', error);
          setSelectedLocation('Nairobi, Kenya');
          setLocationPlaceholder('Nairobi, Kenya');
        }
      );
    } else {
      setSelectedLocation('Nairobi, Kenya');
      setLocationPlaceholder('Nairobi, Kenya');
    }
  }, []);

  const featuredEvents = [
    {
      id: '1',
      title: 'Nairobi Tech Summit 2025',
      image: 'https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg?auto=compress&cs=tinysrgb&w=800',
      description: 'Join industry leaders for innovative tech discussions',
      date: 'Sat, Nov 2',
      location: 'KICC, Nairobi'
    },
    {
      id: '2',
      title: 'Sunset Music Festival',
      image: 'https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=800',
      description: 'Live performances under the stars',
      date: 'Fri, Nov 1',
      location: 'Uhuru Gardens'
    },
    {
      id: '3',
      title: 'Mt. Kenya Hiking Adventure',
      image: 'https://images.pexels.com/photos/618848/pexels-photo-618848.jpeg?auto=compress&cs=tinysrgb&w=800',
      description: 'Experience breathtaking mountain trails',
      date: 'Sun, Nov 3',
      location: 'Mt. Kenya'
    }
  ];

  const upcomingEvents = [
    {
      id: '4',
      title: 'Morning Yoga in the Park',
      image: 'https://images.pexels.com/photos/3822647/pexels-photo-3822647.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Tomorrow',
      time: '6:00 AM',
      location: 'Karura Forest',
      attendees: 45,
      category: 'Fitness',
      price: 'Free'
    },
    {
      id: '5',
      title: 'Startup Networking Mixer',
      image: 'https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Wed, Oct 30',
      time: '6:00 PM',
      location: 'iHub Nairobi',
      attendees: 120,
      category: 'Technology',
      price: 'KES 500'
    },
    {
      id: '6',
      title: 'Weekend Art Exhibition',
      image: 'https://images.pexels.com/photos/1839919/pexels-photo-1839919.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Sat, Nov 2',
      time: '10:00 AM',
      location: 'National Museum',
      attendees: 230,
      category: 'Culture',
      price: 'KES 300'
    },
    {
      id: '7',
      title: 'Food Tasting Tour',
      image: 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Fri, Nov 1',
      time: '5:00 PM',
      location: 'Westlands',
      attendees: 78,
      category: 'Social',
      price: 'KES 1,200'
    },
    {
      id: '8',
      title: 'Beach Clean-Up Drive',
      image: 'https://images.pexels.com/photos/2990644/pexels-photo-2990644.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Sun, Nov 3',
      time: '7:00 AM',
      location: 'Diani Beach',
      attendees: 156,
      category: 'Social',
      price: 'Free'
    },
    {
      id: '9',
      title: 'Jazz Night Live',
      image: 'https://images.pexels.com/photos/1481308/pexels-photo-1481308.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Thu, Oct 31',
      time: '8:00 PM',
      location: 'Alliance Française',
      attendees: 189,
      category: 'Music',
      price: 'KES 800'
    }
  ];

  const cantMissEvents = [
    {
      id: '10',
      title: 'Tech Innovation Summit 2025',
      image: 'https://images.pexels.com/photos/2774556/pexels-photo-2774556.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Fri, Nov 8',
      time: '9:00 AM',
      location: 'Kenyatta Conference Center',
      attendees: 500,
      category: 'Technology',
      price: 'KES 2,000'
    },
    {
      id: '11',
      title: 'Nairobi Food & Wine Festival',
      image: 'https://images.pexels.com/photos/1267320/pexels-photo-1267320.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Sat, Nov 9',
      time: '12:00 PM',
      location: 'Ngong Racecourse',
      attendees: 800,
      category: 'Social',
      price: 'KES 1,500'
    },
    {
      id: '12',
      title: 'Kenya Marathon Championship',
      image: 'https://images.pexels.com/photos/2526878/pexels-photo-2526878.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Sun, Nov 10',
      time: '6:00 AM',
      location: 'Nairobi CBD',
      attendees: 2000,
      category: 'Fitness',
      price: 'Free'
    }
  ];

  const categories = [
    { name: 'All', icon: Users, color: '', count: upcomingEvents.length },
    { name: 'Travel', icon: Plane, color: 'from-blue-500 to-cyan-500', count: 234 },
    { name: 'Sports & Fitness', icon: Dumbbell, color: 'from-green-500 to-emerald-500', count: 189 },
    { name: 'Social Activities', icon: Users, color: 'from-purple-500 to-pink-500', count: 456 },
    { name: 'Music & Culture', icon: Music, color: 'from-red-500 to-orange-500', count: 312 },
    { name: 'Health & Wellbeing', icon: Heart, color: 'from-pink-500 to-rose-500', count: 167 },
    { name: 'Pets & Animals', icon: Dog, color: 'from-amber-500 to-yellow-500', count: 89 },
    { name: 'Autofest', icon: Car, color: 'from-gray-600 to-gray-800', count: 145 },
    { name: 'Hobbies & Interests', icon: Sparkles, color: 'from-indigo-500 to-blue-500', count: 278 },
    { name: 'Coaching & Support', icon: Target, color: 'from-teal-500 to-cyan-500', count: 123 },
    { name: 'Technology', icon: Brain, color: 'from-violet-500 to-purple-500', count: 298 },
    { name: 'Gaming', icon: Gamepad2, color: 'from-fuchsia-500 to-pink-500', count: 201 },
    { name: 'Shopping', icon: ShoppingBag, color: 'from-rose-500 to-red-500', count: 167 },
    { name: 'Religious', icon: Church, color: 'from-blue-600 to-indigo-600', count: 134 },
    { name: 'Dance', icon: Music, color: 'from-orange-500 to-red-500', count: 156 },
    { name: 'Photography', icon: Camera, color: 'from-emerald-500 to-teal-500', count: 112 }
  ];

  const nextBanner = () => {
    setCurrentBanner((prev) => (prev + 1) % featuredEvents.length);
  };

  const prevBanner = () => {
    setCurrentBanner((prev) => (prev - 1 + featuredEvents.length) % featuredEvents.length);
  };

  const scrollCategories = (direction: 'left' | 'right') => {
    if (!categoriesRef.current) return;
    const scrollAmount = 600;
    categoriesRef.current.scrollBy({
      left: direction === 'right' ? scrollAmount : -scrollAmount,
      behavior: 'smooth'
    });
  };

  const handleCategoryScroll = () => {
    if (categoriesRef.current) {
      setShowLeftArrow(categoriesRef.current.scrollLeft > 0);
    }
  };

  React.useEffect(() => {
    const element = categoriesRef.current;
    if (element) {
      element.addEventListener('scroll', handleCategoryScroll);
      return () => element.removeEventListener('scroll', handleCategoryScroll);
    }
  }, []);

  const fetchLocationSuggestions = async (query: string) => {
    if (query.length < 3) {
      setLocationSuggestions([]);
      return;
    }

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=ke`
      );
      const data = await response.json();
      setLocationSuggestions(data);
    } catch (error) {
      console.error('Error fetching location suggestions:', error);
    }
  };

  const handleLocationChange = (value: string) => {
    setSelectedLocation(value);
    setShowLocationSuggestions(true);
    
    // Debounce the API call
    const timeoutId = setTimeout(() => {
      fetchLocationSuggestions(value);
    }, 300);

    return () => clearTimeout(timeoutId);
  };

  const selectLocationSuggestion = (suggestion: {display_name: string}) => {
    setSelectedLocation(suggestion.display_name);
    setShowLocationSuggestions(false);
    setLocationSuggestions([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="sticky top-0 z-50">
        <Navbar onNavigate={onNavigate} currentPage="landing" />
      </div>
      <div className="">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row gap-3 items-center bg-gray-100 rounded-2xl p-4">
            <div className="w-full md:flex-1 flex items-center space-x-3 bg-white rounded-xl px-4 py-3 min-w-0">
              <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
              <input
                type="text"
                placeholder="Search events, categories, or interests..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-500"
              />
            </div>
            <div className="w-full md:w-80 relative">
              <div className="flex items-center space-x-3 bg-white rounded-xl px-4 py-3">
                <MapPin className="w-5 h-5 text-gray-400 flex-shrink-0" />
                <input
                  ref={locationInputRef}
                  type="text"
                  placeholder={locationPlaceholder}
                  value={selectedLocation}
                  onChange={(e) => handleLocationChange(e.target.value)}
                  onFocus={() => {
                    if (selectedLocation === locationPlaceholder) {
                      setSelectedLocation('');
                      setShowLocationSuggestions(true);
                    }
                  }}
                  onBlur={() => {
                    // Delay to allow clicking on suggestions
                    setTimeout(() => {
                      if (selectedLocation === '') {
                        setSelectedLocation(locationPlaceholder);
                      }
                      setShowLocationSuggestions(false);
                    }, 200);
                  }}
                  className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-500"
                />
              </div>
              
              {showLocationSuggestions && locationSuggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 z-50 max-h-64 overflow-y-auto">
                  {locationSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => selectLocationSuggestion(suggestion)}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 flex items-start space-x-3"
                    >
                      <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                      <span className="text-sm text-gray-900">{suggestion.display_name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button className="w-full md:w-12 md:h-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 transform hover:scale-105 transition-all flex-shrink-0">
              <Search className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Organization Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="relative bg-gradient-to-r from-blue-900 via-blue-700 to-blue-600 rounded-3xl overflow-hidden shadow-2xl">
          {/* Animated background pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 50%, white 1px, transparent 1px)',
              backgroundSize: '50px 50px'
            }}></div>
          </div>
          
          <div className="relative px-8 py-10 md:px-12 md:py-14">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              {/* Left Content */}
              <div className="text-white space-y-4">
                <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full mb-2">
                  <Sparkles className="w-5 h-5 text-yellow-300" />
                  <span className="font-semibold text-sm">Niko Free</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-bold leading-tight">
                  Discover Amazing Events
                </h2>
                <p className="text-lg text-blue-100 leading-relaxed">
                  Join millions of people discovering and attending incredible events every day. From concerts to conferences, find your next adventure with Niko Free.
                </p>
                <div className="flex flex-wrap gap-4 pt-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">2M+</p>
                      <p className="text-sm text-blue-100">Active Users</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">10K+</p>
                      <p className="text-sm text-blue-100">Events Monthly</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <Heart className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">98%</p>
                      <p className="text-sm text-blue-100">Satisfaction</p>
                    </div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-3 pt-2">
                  <button 
                    onClick={() => onNavigate('become-partner')}
                    className="px-6 py-3 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transform hover:scale-105 transition-all shadow-lg"
                  >
                    Become a Partner
                  </button>
                  <button 
                    onClick={() => onNavigate('about')}
                    className="px-6 py-3 bg-white/10 backdrop-blur-sm text-white border-2 border-white/30 rounded-xl font-bold hover:bg-white/20 transition-all"
                  >
                    Learn More
                  </button>
                </div>
              </div>

              {/* Right Content - Event Preview Cards */}
              <div className="hidden md:block relative h-80">
                <div className="absolute top-0 right-0 w-56 transform rotate-6 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-white rounded-2xl overflow-hidden shadow-2xl">
                    <img
                      src="https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=400"
                      alt="Event"
                      className="w-full h-32 object-cover"
                    />
                    <div className="p-4">
                      <h3 className="font-bold text-gray-900 text-sm mb-1">Live Music Festival</h3>
                      <p className="text-xs text-gray-600">This Weekend</p>
                    </div>
                  </div>
                </div>
                <div className="absolute top-16 right-16 w-56 transform -rotate-6 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-white rounded-2xl overflow-hidden shadow-2xl">
                    <img
                      src="https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg?auto=compress&cs=tinysrgb&w=400"
                      alt="Event"
                      className="w-full h-32 object-cover"
                    />
                    <div className="p-4">
                      <h3 className="font-bold text-gray-900 text-sm mb-1">Tech Summit 2025</h3>
                      <p className="text-xs text-gray-600">Nov 2 • KICC</p>
                    </div>
                  </div>
                </div>
                <div className="absolute bottom-0 right-8 w-56 transform rotate-3 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-white rounded-2xl overflow-hidden shadow-2xl">
                    <img
                      src="https://images.pexels.com/photos/3822647/pexels-photo-3822647.jpeg?auto=compress&cs=tinysrgb&w=400"
                      alt="Event"
                      className="w-full h-32 object-cover"
                    />
                    <div className="p-4">
                      <h3 className="font-bold text-gray-900 text-sm mb-1">Yoga in the Park</h3>
                      <p className="text-xs text-gray-600">Every Morning</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Decorative Elements */}
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-blue-400 rounded-full opacity-20 blur-3xl"></div>
          <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-blue-300 rounded-full opacity-20 blur-3xl"></div>
        </div>
      </div>

      {/* Featured Events Banner */}

      {/* <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 mb-16">
        <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden">
          <div className="relative h-96 md:h-[500px]">
            <img
              src={featuredEvents[currentBanner].image}
              alt={featuredEvents[currentBanner].title}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
            <div className="absolute bottom-0 left-0 right-0 p-8 md:p-12">
              <div className="max-w-3xl">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                  {featuredEvents[currentBanner].title}
                </h2>
                <p className="text-xl text-gray-200 mb-6">
                  {featuredEvents[currentBanner].description}
                </p>
                <div className="flex flex-wrap gap-4 text-white">
                  <div className="flex items-center space-x-2">
                    <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <MapPin className="w-5 h-5" />
                    </div>
                    <span className="font-medium">{featuredEvents[currentBanner].location}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5" />
                    </div>
                    <span className="font-medium">{featuredEvents[currentBanner].date}</span>
                  </div>
                </div>
                <button
                  onClick={() => onEventClick(featuredEvents[currentBanner].id)}
                  className="mt-6 px-8 py-4 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transform hover:scale-105 transition-all shadow-lg"
                >
                  View Event Details
                </button>
              </div>
            </div>
          </div>

          <button
            onClick={prevBanner}
            className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white transition-colors shadow-lg"
          >
            <ChevronLeft className="w-6 h-6 text-gray-900" />
          </button>
          <button
            onClick={nextBanner}
            className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white transition-colors shadow-lg"
          >
            <ChevronRight className="w-6 h-6 text-gray-900" />
          </button>

          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
            {featuredEvents.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentBanner(index)}
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  currentBanner === index ? 'bg-white w-8' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        </div>
      </div> */}

      <div className=" max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-16">
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-2">Can't Miss!</h2>
          <p className="text-xl text-gray-600">Promoted events you shouldn't miss</p>
        </div>

        <div className="relative">
          <div className="overflow-x-auto scrollbar-hide">
            <div className="flex gap-6 pb-4">
              {cantMissEvents.map((event) => (
                <div
                  key={event.id}
                  className="flex-shrink-0 w-full sm:w-[calc(50%-12px)] lg:w-[calc(25%-18px)] min-w-[280px] cursor-pointer group"
                  onClick={() => onEventClick(event.id)}
                >
                  <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                    <div className="relative h-48">
                      <img
                        src={event.image}
                        alt={event.title}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 opacity-80 group-hover:opacity-100"
                      />
                      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-white/20"></div>
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent transition-opacity duration-300 group-hover:opacity-0"></div>
                      
                      <div className="absolute top-3 left-3 transition-opacity duration-300 group-hover:opacity-0">
                        <span className="px-3 py-1.5 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs font-bold rounded-full shadow-lg flex items-center gap-1">
                          <Sparkles className="w-3.5 h-3.5" />
                          CAN'T MISS
                        </span>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (navigator.share) {
                            navigator.share({
                              title: event.title,
                              text: `Check out this event: ${event.title}`,
                              url: window.location.href,
                            });
                          }
                        }}
                        className="absolute top-3 left-3 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-white shadow-lg z-10"
                      >
                        <Share2 className="w-5 h-5 text-gray-900" />
                      </button>

                      <div className="absolute bottom-0 left-0 right-0 p-4 transition-opacity duration-300 group-hover:opacity-0">
                        <h3 className="text-xl font-bold text-white mb-2 line-clamp-2">
                          {event.title}
                        </h3>
                      </div>
                    </div>

                    <div className="p-4">
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-gray-600 text-sm">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{event.date} • {event.time}</span>
                        </div>
                        <div className="flex items-center text-gray-600 text-sm">
                          <MapPin className="w-4 h-4 mr-2" />
                          <span>{event.location}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="flex -space-x-2">
                            <img
                              src={`https://i.pravatar.cc/150?img=${(parseInt(event.id) * 3) % 70}`}
                              alt="Attendee"
                              className="w-6 h-6 rounded-full border-2 border-white"
                            />
                            <img
                              src={`https://i.pravatar.cc/150?img=${(parseInt(event.id) * 3 + 1) % 70}`}
                              alt="Attendee"
                              className="w-6 h-6 rounded-full border-2 border-white"
                            />
                            <img
                              src={`https://i.pravatar.cc/150?img=${(parseInt(event.id) * 3 + 2) % 70}`}
                              alt="Attendee"
                              className="w-6 h-6 rounded-full border-2 border-white"
                            />
                          </div>
                          <span className="text-sm text-gray-600">+{event.attendees - 3} attending</span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEventClick(event.id);
                        }}
                        className="w-full px-4 py-2.5 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors"
                      >
                        Get Tickets • {event.price}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Browse by Category</h2>
          <p className="text-xl text-gray-600">Find events that match your interests</p>
        </div>

        <div className="relative">
          <div className="overflow-hidden">
            <div 
              ref={categoriesRef}
              className="flex gap-4 snap-x snap-mandatory overflow-x-auto pb-6 hide-scrollbar"
            >
              {categories.map((category, index) => {
                const Icon = category.icon;
                const isSelected = selectedCategory === category.name || (!selectedCategory && index === 0);
                return (
                  <button
                    key={index}
                    onClick={() => setSelectedCategory(index === 0 ? null : category.name)}
                    className={`flex-none snap-start group flex flex-col items-center rounded-xl px-4 py-5 transition-all duration-200 relative`}
                  >
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gray-100 mb-2 group-hover:scale-110 transition-transform">
                      <Icon className="w-6 h-6 text-blue-500" />
                    </div>
                    <span className={`text-sm mb-1 text-center whitespace-nowrap ${isSelected ? 'font-bold text-gray-900' : 'font-medium text-gray-900 group-hover:font-bold'}`}>{category.name}</span>
                    <span className="text-xs text-gray-500 text-center whitespace-nowrap">{category.count} events</span>
                    <span className={`absolute left-2 right-2 bottom-0 h-0.5 rounded-full ${isSelected ? 'bg-blue-600' : 'bg-gray-200'}`} />
                  </button>
                );
              })}
            </div>
          </div>
          <button
            onClick={() => scrollCategories('left')}
            className={`absolute left-0 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white shadow-lg hover:bg-gray-50 transition-all ${showLeftArrow ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          >
            <ChevronLeft className="w-6 h-6 text-gray-600" />
          </button>
          <button
            onClick={() => scrollCategories('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white shadow-lg hover:bg-gray-50 transition-colors"
          >
            <ChevronRight className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 mt-4">
          {(selectedCategory ? upcomingEvents.filter(event => event.category === selectedCategory) : upcomingEvents)
            .map(event => (
              <div key={event.id} className="bg-white rounded-xl p-6 transition-colors duration-200 hover:bg-gray-50">
                <EventCard
                  {...event}
                  onClick={onEventClick}
                />
              </div>
            ))}
        </div>
        {(selectedCategory && upcomingEvents.filter(event => event.category === selectedCategory).length === 0) && (
          <div className="text-center py-12">
            <p className="text-gray-600">No events found in this category</p>
          </div>
        )}
      </div>

      <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Host Your Own Event?
          </h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Join thousands of organizers using Niko Free to create memorable experiences.
            Start for free and reach your community today.
          </p>
          <button
            onClick={() => onNavigate('become-partner')}
            className="px-10 py-4 bg-white text-blue-600 rounded-xl font-bold text-lg hover:bg-blue-50 transform hover:scale-105 transition-all shadow-xl"
          >
            Become a Partner
          </button>
        </div>
      </div>

      <Footer />
    </div>
  );
}
