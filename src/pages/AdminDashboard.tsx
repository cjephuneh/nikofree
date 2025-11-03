import { Users, Calendar, DollarSign, TrendingUp, CheckCircle, XCircle, Clock, Ban, Settings } from 'lucide-react';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

interface AdminDashboardProps {
  onNavigate: (page: string) => void;
}

export default function AdminDashboard({ onNavigate }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'partners' | 'events' | 'settings'>('overview');

  const stats = [
    { label: 'Total Users', value: '15,234', icon: Users, color: 'from-blue-500 to-blue-600', change: '+12% this month' },
    { label: 'Active Partners', value: '342', icon: Users, color: 'from-green-500 to-green-600', change: '+8% this month' },
    { label: 'Total Events', value: '1,847', icon: Calendar, color: 'from-purple-500 to-purple-600', change: '+156 this month' },
    { label: 'Platform Revenue', value: 'KES 1.2M', icon: DollarSign, color: 'from-orange-500 to-orange-600', change: '7% commission' }
  ];

  const pendingPartners = [
    {
      id: '1',
      name: 'Tech Hub Africa',
      email: 'contact@techhub.africa',
      category: 'Technology',
      submittedDate: '2 hours ago',
      status: 'pending'
    },
    {
      id: '2',
      name: 'Fitness Pro Kenya',
      email: 'info@fitnesspro.ke',
      category: 'Sports & Fitness',
      submittedDate: '5 hours ago',
      status: 'pending'
    }
  ];

  const pendingEvents = [
    {
      id: '1',
      title: 'Nairobi Innovation Week',
      partner: 'Tech Hub Africa',
      category: 'Technology',
      date: 'Nov 15, 2025',
      status: 'pending'
    },
    {
      id: '2',
      title: 'Marathon for Health',
      partner: 'Fitness Pro Kenya',
      category: 'Sports',
      date: 'Nov 10, 2025',
      status: 'pending'
    }
  ];

  const approvedPartners = [
    {
      id: '3',
      name: 'Creative Arts Kenya',
      totalEvents: 12,
      totalRevenue: 'KES 284,700',
      rating: 4.8,
      status: 'active'
    },
    {
      id: '4',
      name: 'Music Matters',
      totalEvents: 8,
      totalRevenue: 'KES 156,000',
      rating: 4.6,
      status: 'active'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onNavigate={onNavigate} />

      <div className="bg-gradient-to-br from-gray-900 via-blue-900 to-black py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-4 md:space-y-0">
            <div className="text-white">
              <h1 className="text-4xl font-bold mb-2">Admin Dashboard</h1>
              <p className="text-gray-300 text-lg">Manage platform operations and oversight</p>
            </div>
            <div className="flex space-x-3">
              <button className="px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl font-semibold hover:bg-white/30 transition-all flex items-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </button>
            </div>
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
                <TrendingUp className="w-5 h-5" />
                <span>Overview</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('partners')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'partners'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Users className="w-5 h-5" />
                <span>Partners</span>
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
                <span>Events</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === 'settings'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>Settings</span>
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
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">Pending Approvals</h3>
                  <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-semibold">
                    {pendingPartners.length + pendingEvents.length}
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-gray-900">Partner Applications</p>
                      <span className="text-sm text-gray-600">{pendingPartners.length} pending</span>
                    </div>
                    <button
                      onClick={() => setActiveTab('partners')}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Review now →
                    </button>
                  </div>
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-gray-900">Event Submissions</p>
                      <span className="text-sm text-gray-600">{pendingEvents.length} pending</span>
                    </div>
                    <button
                      onClick={() => setActiveTab('events')}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Review now →
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Activity</h3>
                <div className="space-y-4">
                  {[
                    { action: 'Partner approved', name: 'Creative Arts Kenya', time: '1 hour ago' },
                    { action: 'Event published', name: 'Jazz Night Live', time: '3 hours ago' },
                    { action: 'New user registered', name: 'John Doe', time: '5 hours ago' }
                  ].map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-xl">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{activity.action}</p>
                        <p className="text-sm text-gray-600">{activity.name}</p>
                      </div>
                      <span className="text-xs text-gray-500">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'partners' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Pending Partner Applications</h2>
              <div className="space-y-4">
                {pendingPartners.map((partner) => (
                  <div
                    key={partner.id}
                    className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all p-6 border border-gray-100"
                  >
                    <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{partner.name}</h3>
                          <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-semibold flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>PENDING</span>
                          </span>
                        </div>
                        <p className="text-gray-600 mb-2">{partner.email}</p>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                          <span>Category: {partner.category}</span>
                          <span>Submitted: {partner.submittedDate}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-6 py-2.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4" />
                          <span>Approve</span>
                        </button>
                        <button className="px-6 py-2.5 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center space-x-2">
                          <XCircle className="w-4 h-4" />
                          <span>Reject</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Active Partners</h2>
              <div className="space-y-4">
                {approvedPartners.map((partner) => (
                  <div
                    key={partner.id}
                    className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all p-6 border border-gray-100"
                  >
                    <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{partner.name}</h3>
                          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                            ACTIVE
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-6 text-sm text-gray-600 mt-3">
                          <span>{partner.totalEvents} events</span>
                          <span>Revenue: {partner.totalRevenue}</span>
                          <span>Rating: {partner.rating}/5.0</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-6 py-2.5 border-2 border-gray-200 text-gray-700 rounded-lg font-semibold hover:border-blue-500 hover:text-blue-600 transition-all">
                          View Details
                        </button>
                        <button className="px-6 py-2.5 border-2 border-red-200 text-red-600 rounded-lg font-semibold hover:border-red-500 transition-all flex items-center space-x-2">
                          <Ban className="w-4 h-4" />
                          <span>Suspend</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Pending Event Approvals</h2>
            <div className="space-y-4">
              {pendingEvents.map((event) => (
                <div
                  key={event.id}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all p-6 border border-gray-100"
                >
                  <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-900">{event.title}</h3>
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                          {event.category}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <span>By: {event.partner}</span>
                        <span>Date: {event.date}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="px-6 py-2.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4" />
                        <span>Approve</span>
                      </button>
                      <button className="px-6 py-2.5 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center space-x-2">
                        <XCircle className="w-4 h-4" />
                        <span>Reject</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Settings</h2>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Categories Management</h3>
              <p className="text-gray-600 mb-4">Manage event categories and classifications</p>
              <button className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                Manage Categories
              </button>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Locations Management</h3>
              <p className="text-gray-600 mb-4">Add or remove supported locations</p>
              <button className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                Manage Locations
              </button>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Commission Settings</h3>
              <p className="text-gray-600 mb-4">Current platform commission: 7%</p>
              <button className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                Adjust Commission
              </button>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
