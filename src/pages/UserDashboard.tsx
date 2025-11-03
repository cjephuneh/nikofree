import { Calendar, Heart, History, Download, QrCode, LogOut, User, Settings, Bell } from 'lucide-react';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface UserDashboardProps {
  onNavigate: (page: string) => void;
}

export default function UserDashboard({ onNavigate }: UserDashboardProps) {
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past' | 'bucketlist'>('upcoming');

  const upcomingEvents = [
    {
      id: '1',
      title: 'Nairobi Tech Summit 2025',
      image: 'https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg?auto=compress&cs=tinysrgb&w=400',
      date: 'Sat, Nov 2',
      time: '9:00 AM',
      location: 'KICC, Nairobi',
      ticketId: 'TKT-2025-001',
      hasQR: true
    },
    {
      id: '2',
      title: 'Morning Yoga in the Park',
      image: 'https://images.pexels.com/photos/3822647/pexels-photo-3822647.jpeg?auto=compress&cs=tinysrgb&w=400',
      date: 'Tomorrow',
      time: '6:00 AM',
      location: 'Karura Forest',
      ticketId: 'TKT-2025-002',
      hasQR: true
    }
  ];

  const pastEvents = [
    {
      id: '3',
      title: 'Jazz Night Live',
      image: 'https://images.pexels.com/photos/1481308/pexels-photo-1481308.jpeg?auto=compress&cs=tinysrgb&w=400',
      date: 'Oct 25, 2025',
      location: 'Alliance Française',
      rating: 5
    }
  ];

  const bucketlistEvents = [
    {
      id: '4',
      title: 'Sunset Music Festival',
      image: 'https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=400',
      date: 'Fri, Nov 1',
      location: 'Uhuru Gardens',
      price: 'KES 800'
    },
    {
      id: '5',
      title: 'Mt. Kenya Hiking Adventure',
      image: 'https://images.pexels.com/photos/618848/pexels-photo-618848.jpeg?auto=compress&cs=tinysrgb&w=400',
      date: 'Sun, Nov 3',
      location: 'Mt. Kenya',
      price: 'Free'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onNavigate={onNavigate} />

      <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-6">
              <div className="w-24 h-24 bg-white rounded-2xl flex items-center justify-center shadow-lg">
                <User className="w-12 h-12 text-blue-600" />
              </div>
              <div className="text-white">
                <h1 className="text-4xl font-bold mb-2">Welcome back, Alex!</h1>
                <p className="text-blue-100 text-lg">Your next adventure awaits</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-white hover:bg-white/30 transition-colors">
                <Bell className="w-5 h-5" />
              </button>
              <button className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-white hover:bg-white/30 transition-colors">
                <Settings className="w-5 h-5" />
              </button>
              <button
                onClick={() => onNavigate('landing')}
                className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-white hover:bg-white/30 transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="bg-white rounded-2xl shadow-lg p-2">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('upcoming')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'upcoming'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Calendar className="w-5 h-5" />
                <span>Upcoming</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('past')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'past'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <History className="w-5 h-5" />
                <span>Past Events</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('bucketlist')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'bucketlist'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Heart className="w-5 h-5" />
                <span>Bucketlist</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upcoming' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Upcoming Events</h2>
            <div className="space-y-4">
              {upcomingEvents.map((event) => (
                <div
                  key={event.id}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all p-6 border border-gray-100"
                >
                  <div className="flex flex-col md:flex-row gap-6">
                    <img
                      src={event.image}
                      alt={event.title}
                      className="w-full md:w-48 h-32 object-cover rounded-xl"
                    />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{event.title}</h3>
                      <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4 text-blue-600" />
                          <span>{event.date} • {event.time}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <QrCode className="w-4 h-4 text-blue-600" />
                          <span className="font-mono text-xs">{event.ticketId}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex md:flex-col gap-2">
                      <button className="flex-1 md:flex-none px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
                        <QrCode className="w-4 h-4" />
                        <span>View Ticket</span>
                      </button>
                      <button className="flex-1 md:flex-none px-6 py-3 border-2 border-gray-200 text-gray-700 rounded-xl font-semibold hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center space-x-2">
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'past' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Event History</h2>
            <div className="space-y-4">
              {pastEvents.map((event) => (
                <div
                  key={event.id}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all p-6 border border-gray-100"
                >
                  <div className="flex flex-col md:flex-row gap-6">
                    <img
                      src={event.image}
                      alt={event.title}
                      className="w-full md:w-48 h-32 object-cover rounded-xl"
                    />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{event.title}</h3>
                      <p className="text-sm text-gray-600 mb-3">{event.date}</p>
                      <div className="flex space-x-1">
                        {[...Array(event.rating)].map((_, i) => (
                          <div key={i} className="w-5 h-5 text-yellow-400">★</div>
                        ))}
                      </div>
                    </div>
                    <div className="flex md:flex-col gap-2">
                      <button className="flex-1 md:flex-none px-6 py-3 border-2 border-gray-200 text-gray-700 rounded-xl font-semibold hover:border-blue-500 hover:text-blue-600 transition-all">
                        Rate Event
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'bucketlist' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Bucketlist</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {bucketlistEvents.map((event) => (
                <div
                  key={event.id}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all overflow-hidden border border-gray-100"
                >
                  <img
                    src={event.image}
                    alt={event.title}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{event.title}</h3>
                    <p className="text-sm text-gray-600 mb-4">{event.date}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-blue-600">{event.price}</span>
                      <button className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                        Book Now
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
