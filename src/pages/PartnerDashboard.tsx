import { Plus, Calendar, Users, DollarSign, TrendingUp, BarChart3, Download, Eye, Edit, Trash2, Zap } from 'lucide-react';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface PartnerDashboardProps {
  onNavigate: (page: string) => void;
}

export default function PartnerDashboard({ onNavigate }: PartnerDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'events' | 'analytics'>('overview');

  const stats = [
    { label: 'Total Events', value: '12', icon: Calendar, color: 'from-blue-500 to-blue-600', change: '+2 this month' },
    { label: 'Total Attendees', value: '2,847', icon: Users, color: 'from-green-500 to-green-600', change: '+15% vs last month' },
    { label: 'Total Revenue', value: 'KES 284,700', icon: DollarSign, color: 'from-purple-500 to-purple-600', change: 'After 7% commission' },
    { label: 'Avg. Rating', value: '4.8', icon: TrendingUp, color: 'from-orange-500 to-orange-600', change: 'From 234 reviews' }
  ];

  const events = [
    {
      id: '1',
      title: 'Nairobi Tech Summit 2025',
      status: 'upcoming',
      date: 'Nov 2, 2025',
      attendees: 847,
      revenue: 'KES 158,000',
      ticketsSold: 847,
      totalTickets: 1000
    },
    {
      id: '2',
      title: 'Startup Networking Mixer',
      status: 'upcoming',
      date: 'Oct 30, 2025',
      attendees: 120,
      revenue: 'KES 46,500',
      ticketsSold: 120,
      totalTickets: 150
    },
    {
      id: '3',
      title: 'Jazz Night Live',
      status: 'past',
      date: 'Oct 25, 2025',
      attendees: 189,
      revenue: 'KES 80,200',
      ticketsSold: 189,
      totalTickets: 200
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onNavigate={onNavigate} />

      <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-4 md:space-y-0">
            <div className="text-white">
              <h1 className="text-4xl font-bold mb-2">Partner Dashboard</h1>
              <p className="text-blue-100 text-lg">Manage your events and track performance</p>
            </div>
            <button
              onClick={() => onNavigate('create-event')}
              className="px-8 py-4 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transform hover:scale-105 transition-all shadow-xl flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Create New Event</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="bg-white rounded-2xl shadow-lg p-2">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'overview'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <BarChart3 className="w-5 h-5" />
                <span>Overview</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('events')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'events'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Calendar className="w-5 h-5" />
                <span>My Events</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'analytics'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Analytics</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <div
                    key={index}
                    className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all border border-gray-100"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
                    <p className="text-xs text-gray-500">{stat.change}</p>
                  </div>
                );
              })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Activity</h3>
                <div className="space-y-4">
                  {[
                    { action: 'New ticket purchased', event: 'Tech Summit', time: '2 hours ago' },
                    { action: 'Event approved', event: 'Networking Mixer', time: '5 hours ago' },
                    { action: '10 new attendees', event: 'Jazz Night', time: '1 day ago' }
                  ].map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-xl">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{activity.action}</p>
                        <p className="text-sm text-gray-600">{activity.event}</p>
                      </div>
                      <span className="text-xs text-gray-500">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-6 shadow-lg text-white">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-xl font-bold mb-2">Boost Your Events</h3>
                    <p className="text-blue-100">Get more visibility and attendees</p>
                  </div>
                  <Zap className="w-8 h-8 text-yellow-300" />
                </div>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-center space-x-2">
                    <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">✓</div>
                    <span className="text-sm">Featured on homepage</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">✓</div>
                    <span className="text-sm">Priority in search results</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">✓</div>
                    <span className="text-sm">Social media promotion</span>
                  </li>
                </ul>
                <button className="w-full py-3 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transition-colors">
                  Start from KES 400/day
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">My Events</h2>
              <button
                onClick={() => onNavigate('create-event')}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>New Event</span>
              </button>
            </div>

            <div className="space-y-4">
              {events.map((event) => (
                <div
                  key={event.id}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all p-6 border border-gray-100"
                >
                  <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-900">{event.title}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          event.status === 'upcoming'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {event.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-4">{event.date}</p>
                      <div className="flex flex-wrap gap-6 text-sm">
                        <div className="flex items-center space-x-2">
                          <Users className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{event.attendees} attendees</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <DollarSign className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{event.revenue}</span>
                        </div>
                      </div>
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-600">Tickets sold</span>
                          <span className="font-semibold">{event.ticketsSold}/{event.totalTickets}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(event.ticketsSold / event.totalTickets) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <div className="flex lg:flex-col gap-2 w-full lg:w-auto">
                      <button className="flex-1 lg:flex-none px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
                        <Eye className="w-4 h-4" />
                        <span>View</span>
                      </button>
                      <button className="flex-1 lg:flex-none px-6 py-2.5 border-2 border-gray-200 text-gray-700 rounded-lg font-semibold hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center space-x-2">
                        <Edit className="w-4 h-4" />
                        <span>Edit</span>
                      </button>
                      <button className="flex-1 lg:flex-none px-6 py-2.5 border-2 border-gray-200 text-gray-700 rounded-lg font-semibold hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center space-x-2">
                        <Download className="w-4 h-4" />
                        <span>Export</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Analytics & Insights</h2>

            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Revenue Overview</h3>
              <div className="h-64 bg-gray-50 rounded-xl flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p>Chart visualization coming soon</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-6">Top Performing Events</h3>
                <div className="space-y-4">
                  {[
                    { name: 'Tech Summit', revenue: 'KES 158,000', attendees: 847 },
                    { name: 'Jazz Night', revenue: 'KES 80,200', attendees: 189 },
                    { name: 'Networking Mixer', revenue: 'KES 46,500', attendees: 120 }
                  ].map((event, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-semibold text-gray-900">{event.name}</p>
                        <p className="text-sm text-gray-600">{event.attendees} attendees</p>
                      </div>
                      <p className="font-bold text-blue-600">{event.revenue}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-6">Attendee Demographics</h3>
                <div className="h-48 bg-gray-50 rounded-xl flex items-center justify-center">
                  <p className="text-gray-500">Demographics chart</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
