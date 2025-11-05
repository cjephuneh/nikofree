import { Users, Calendar, DollarSign, CheckCircle, XCircle, Clock, Ban, Settings, Menu, X, Search, User, LogOut, Shield, FileText, BarChart3 } from 'lucide-react';
import { useState } from 'react';

interface AdminDashboardProps {
  onNavigate: (page: string) => void;
}

export default function AdminDashboard({ onNavigate }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'partners' | 'events' | 'settings'>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

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
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 relative">
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
      
      <div className="relative z-10 flex min-h-screen w-full">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <aside className={`fixed lg:sticky top-0 left-0 z-50 h-screen w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 lg:transform-none ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}>
        <div className="h-full flex flex-col">
          {/* Sidebar Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="font-bold text-gray-900">Admin Portal</h2>
                  <p className="text-xs text-gray-500">System Control</p>
                </div>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Sidebar Menu */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              <button
                onClick={() => setActiveTab('overview')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'overview'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <BarChart3 className="w-5 h-5" />
                <span>Overview</span>
              </button>

              <button
                onClick={() => setActiveTab('partners')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'partners'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Users className="w-5 h-5" />
                <span>Partners</span>
              </button>

              <button
                onClick={() => setActiveTab('events')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'events'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Calendar className="w-5 h-5" />
                <span>Events</span>
              </button>

              <button
                onClick={() => setActiveTab('settings')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'settings'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </button>

              <button
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-gray-700 hover:bg-gray-100 transition-all"
              >
                <FileText className="w-5 h-5" />
                <span>Reports</span>
              </button>

              <button
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-gray-700 hover:bg-gray-100 transition-all"
              >
                <DollarSign className="w-5 h-5" />
                <span>Revenue</span>
              </button>
            </div>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top Navigation */}
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
          <div className="px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              {/* Left - Menu & Title */}
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden text-gray-500 hover:text-gray-700"
                >
                  <Menu className="w-6 h-6" />
                </button>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">
                    {activeTab === 'overview' && 'Dashboard Overview'}
                    {activeTab === 'partners' && 'Partner Management'}
                    {activeTab === 'events' && 'Event Management'}
                    {activeTab === 'settings' && 'Platform Settings'}
                  </h1>
                  <p className="text-sm text-gray-500 hidden sm:block">Manage platform operations</p>
                </div>
              </div>

              {/* Center - Search Bar */}
              <div className="hidden md:flex flex-1 max-w-md mx-8">
                <div className="relative w-full">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-gray-100 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
                  />
                </div>
              </div>

              {/* Right - Account Menu */}
              <div className="relative">
                <button
                  onClick={() => setAccountMenuOpen(!accountMenuOpen)}
                  className="flex items-center space-x-3 p-2 hover:bg-gray-100 rounded-xl transition-colors"
                >
                  <img
                    src="https://i.pravatar.cc/150?img=60"
                    alt="Admin"
                    className="w-9 h-9 rounded-full object-cover"
                  />
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-semibold text-gray-900">System Admin</p>
                    <p className="text-xs text-gray-500">Administrator</p>
                  </div>
                </button>

                {/* Account Dropdown */}
                {accountMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-sm font-semibold text-gray-900">System Admin</p>
                      <p className="text-xs text-gray-500">admin@nikofree.com</p>
                    </div>
                    <button className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2">
                      <User className="w-4 h-4" />
                      <span>My Profile</span>
                    </button>
                    <button className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2">
                      <Settings className="w-4 h-4" />
                      <span>Settings</span>
                    </button>
                    <div className="border-t border-gray-100 mt-2 pt-2">
                      <button 
                        onClick={() => onNavigate('landing')}
                        className="w-full px-4 py-2.5 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Log Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="flex-1 overflow-x-hidden p-6 lg:p-8">
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
        </main>
      </div>
      </div>
    </div>
  );
}
