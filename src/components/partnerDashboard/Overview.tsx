import { TrendingUp, DollarSign, Wallet, ArrowDownRight, Calendar, Users, Eye, Download, ArrowUpRight, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';

interface OverviewProps {
  onWithdrawClick?: () => void;
}

export default function Overview({ onWithdrawClick }: OverviewProps) {
  const [currentEventsPage, setCurrentEventsPage] = useState(0);
  const [historyEventsPage, setHistoryEventsPage] = useState(0);
  const eventsPerPage = 5;

  // Financial Stats - Net earnings after 7% deduction
  const financialStats = [
    {
      label: 'Net Earnings',
      value: 'Ksh 186,000',
      subtext: 'After 7% deduction',
      icon: TrendingUp,
      color: 'from-green-500 to-emerald-600',
      change: '+12.5%',
      isPositive: true
    },
    {
      label: 'Amount Withdrawn',
      value: 'Ksh 150,000',
      subtext: 'Total withdrawals',
      icon: ArrowDownRight,
      color: 'from-blue-500 to-cyan-600',
    },
    {
      label: 'Current Balance',
      value: 'Ksh 36,000',
      subtext: 'Available to withdraw',
      icon: Wallet,
      color: 'from-purple-500 to-pink-600',
    },
    {
      label: 'Gross Revenue',
      value: 'Ksh 200,000',
      subtext: 'Before deductions',
      icon: DollarSign,
      color: 'from-orange-500 to-red-600',
    }
  ];

  // Recent Withdrawals
  const withdrawals = [
    {
      id: '1',
      method: 'M-Pesa',
      phone: '+254 712 ***678',
      amount: 'Ksh 50,000',
      date: 'Dec 5, 2024',
      time: '2:45 PM',
      status: 'Completed',
      type: 'mpesa'
    },
    {
      id: '2',
      method: 'Bank Transfer',
      account: 'Equity Bank ***4567',
      amount: 'Ksh 100,000',
      date: 'Dec 1, 2024',
      time: '10:30 AM',
      status: 'Completed',
      type: 'bank'
    }
  ];

  // Current Events (Active)
  const currentEvents = [
    {
      id: '1',
      title: 'Tech Conference 2024',
      image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400&h=300&fit=crop',
      date: 'Dec 15, 2024',
      attendees: '245/300',
      ticketsSold: 245,
      totalTickets: 300,
      grossRevenue: 'Ksh 73,500',
      netEarnings: 'Ksh 68,355',
      views: '1,234',
      status: 'active'
    },
    {
      id: '2',
      title: 'Startup Meetup',
      image: 'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=400&h=300&fit=crop',
      date: 'Dec 20, 2024',
      attendees: '89/150',
      ticketsSold: 89,
      totalTickets: 150,
      grossRevenue: 'Ksh 26,700',
      netEarnings: 'Ksh 24,831',
      views: '892',
      status: 'active'
    },
    {
      id: '3',
      title: 'Innovation Summit',
      image: 'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=400&h=300&fit=crop',
      date: 'Jan 10, 2025',
      attendees: '156/200',
      ticketsSold: 156,
      totalTickets: 200,
      grossRevenue: 'Ksh 62,400',
      netEarnings: 'Ksh 58,032',
      views: '2,145',
      status: 'active'
    },
    {
      id: '4',
      title: 'Digital Marketing Workshop',
      image: 'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=400&h=300&fit=crop',
      date: 'Jan 15, 2025',
      attendees: '67/100',
      ticketsSold: 67,
      totalTickets: 100,
      grossRevenue: 'Ksh 20,100',
      netEarnings: 'Ksh 18,693',
      views: '567',
      status: 'active'
    },
    {
      id: '5',
      title: 'AI & Machine Learning Bootcamp',
      image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop',
      date: 'Jan 22, 2025',
      attendees: '123/150',
      ticketsSold: 123,
      totalTickets: 150,
      grossRevenue: 'Ksh 49,200',
      netEarnings: 'Ksh 45,756',
      views: '1,678',
      status: 'active'
    },
    {
      id: '6',
      title: 'Networking Night',
      image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=400&h=300&fit=crop',
      date: 'Jan 25, 2025',
      attendees: '98/120',
      ticketsSold: 98,
      totalTickets: 120,
      grossRevenue: 'Ksh 29,400',
      netEarnings: 'Ksh 27,342',
      views: '743',
      status: 'active'
    }
  ];

  // Events History (Completed)
  const eventHistory = [
    {
      id: '1',
      title: 'Web Development Bootcamp',
      image: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=300&fit=crop',
      date: 'Nov 28, 2024',
      attendees: '187/200',
      grossRevenue: 'Ksh 74,800',
      netEarnings: 'Ksh 69,564',
      views: '2,341',
      status: 'completed'
    },
    {
      id: '2',
      title: 'Business Strategy Summit',
      image: 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=300&fit=crop',
      date: 'Nov 15, 2024',
      attendees: '234/250',
      grossRevenue: 'Ksh 93,600',
      netEarnings: 'Ksh 87,048',
      views: '3,567',
      status: 'completed'
    },
    {
      id: '3',
      title: 'Creative Design Workshop',
      image: 'https://images.unsplash.com/photo-1542744094-3a31f272c490?w=400&h=300&fit=crop',
      date: 'Oct 30, 2024',
      attendees: '145/150',
      grossRevenue: 'Ksh 58,000',
      netEarnings: 'Ksh 53,940',
      views: '1,892',
      status: 'completed'
    },
    {
      id: '4',
      title: 'Cybersecurity Conference',
      image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&h=300&fit=crop',
      date: 'Oct 12, 2024',
      attendees: '167/180',
      grossRevenue: 'Ksh 66,800',
      netEarnings: 'Ksh 62,124',
      views: '2,134',
      status: 'completed'
    },
    {
      id: '5',
      title: 'Mobile App Development',
      image: 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop',
      date: 'Sep 25, 2024',
      attendees: '112/120',
      grossRevenue: 'Ksh 44,800',
      netEarnings: 'Ksh 41,664',
      views: '1,456',
      status: 'completed'
    },
    {
      id: '6',
      title: 'E-commerce Masterclass',
      image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop',
      date: 'Sep 10, 2024',
      attendees: '198/200',
      grossRevenue: 'Ksh 79,200',
      netEarnings: 'Ksh 73,656',
      views: '2,789',
      status: 'completed'
    }
  ];

  const currentEventsSlides = [];
  for (let i = 0; i < currentEvents.length; i += eventsPerPage) {
    currentEventsSlides.push(currentEvents.slice(i, i + eventsPerPage));
  }

  const historyEventsSlides = [];
  for (let i = 0; i < eventHistory.length; i += eventsPerPage) {
    historyEventsSlides.push(eventHistory.slice(i, i + eventsPerPage));
  }

  return (
    <div className="space-y-6">
      {/* Financial Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {financialStats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm hover:shadow-lg transition-all border border-gray-100 dark:border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                {stat.change && (
                  <span className={`text-sm font-semibold px-2 py-1 rounded-full ${
                    stat.isPositive ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {stat.change}
                  </span>
                )}
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">{stat.label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{stat.value}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{stat.subtext}</p>
            </div>
          );
        })}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button 
          onClick={onWithdrawClick}
          className="bg-gradient-to-r from-[#27aae2] to-[#1e8bb8] text-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all group"
        >
          <div className="flex items-center justify-between">
            <div className="text-left">
              <h3 className="text-lg font-bold mb-1">Withdraw Funds</h3>
              <p className="text-blue-100 text-sm">Instant to M-Pesa or Bank</p>
            </div>
            <ArrowUpRight className="w-8 h-8 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
          </div>
        </button>
        
        <button className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-sm hover:shadow-lg hover:border-[#27aae2] transition-all group">
          <div className="flex items-center justify-between">
            <div className="text-left">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">Download Statement</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">PDF or Excel format</p>
            </div>
            <Download className="w-8 h-8 text-gray-700 dark:text-gray-300 group-hover:translate-y-1 transition-transform" />
          </div>
        </button>
      </div>

      {/* Recent Withdrawals */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Recent Withdrawals</h3>
          <button className="text-[#27aae2] hover:text-[#1e8bb8] font-semibold text-sm">View All</button>
        </div>
        <div className="space-y-3">
          {withdrawals.map((withdrawal) => (
            <div key={withdrawal.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-[#27aae2]/10 dark:bg-[#27aae2]/20 rounded-xl flex items-center justify-center">
                  {withdrawal.type === 'mpesa' ? (
                    <Wallet className="w-6 h-6 text-[#27aae2]" />
                  ) : (
                    <DollarSign className="w-6 h-6 text-[#27aae2]" />
                  )}
                </div>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">{withdrawal.method}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {withdrawal.phone || withdrawal.account} • {withdrawal.date} at {withdrawal.time}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-gray-900 dark:text-white text-lg">{withdrawal.amount}</p>
                <span className="text-xs px-2 py-1 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded-full font-semibold">
                  {withdrawal.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Current Events Slideshow */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Current Events</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentEventsPage(Math.max(0, currentEventsPage - 1))}
              disabled={currentEventsPage === 0}
              className={`p-2 rounded-lg ${
                currentEventsPage === 0
                  ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {currentEventsPage + 1} / {currentEventsSlides.length}
            </span>
            <button
              onClick={() => setCurrentEventsPage(Math.min(currentEventsSlides.length - 1, currentEventsPage + 1))}
              disabled={currentEventsPage === currentEventsSlides.length - 1}
              className={`p-2 rounded-lg ${
                currentEventsPage === currentEventsSlides.length - 1
                  ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {currentEventsSlides[currentEventsPage]?.map((event) => (
            <div
              key={event.id}
              className="group cursor-pointer bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden hover:shadow-lg transition-all"
            >
              <div className="relative h-32">
                <img
                  src={event.image}
                  alt={event.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                  ACTIVE
                </div>
              </div>
              <div className="p-3">
                <h4 className="font-bold text-gray-900 dark:text-white mb-1 line-clamp-1 text-sm">{event.title}</h4>
                <div className="flex items-center text-xs text-gray-600 dark:text-gray-400 mb-2">
                  <Calendar className="w-3 h-3 mr-1" />
                  {event.date}
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 dark:text-gray-400">Net Earnings</span>
                    <span className="font-bold text-green-600 dark:text-green-400">{event.netEarnings}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 dark:text-gray-400">Gross Revenue</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{event.grossRevenue}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Users className="w-3 h-3 mr-1" />
                      <span>Attendees</span>
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">{event.attendees}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Eye className="w-3 h-3 mr-1" />
                      <span>Views</span>
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">{event.views}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-[#27aae2] h-2 rounded-full transition-all"
                      style={{ width: `${(event.ticketsSold / event.totalTickets) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 text-right">
                    {event.ticketsSold}/{event.totalTickets} tickets sold
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Events History Slideshow */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Events History</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setHistoryEventsPage(Math.max(0, historyEventsPage - 1))}
              disabled={historyEventsPage === 0}
              className={`p-2 rounded-lg ${
                historyEventsPage === 0
                  ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {historyEventsPage + 1} / {historyEventsSlides.length}
            </span>
            <button
              onClick={() => setHistoryEventsPage(Math.min(historyEventsSlides.length - 1, historyEventsPage + 1))}
              disabled={historyEventsPage === historyEventsSlides.length - 1}
              className={`p-2 rounded-lg ${
                historyEventsPage === historyEventsSlides.length - 1
                  ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {historyEventsSlides[historyEventsPage]?.map((event) => (
            <div
              key={event.id}
              className="group cursor-pointer bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden hover:shadow-lg transition-all"
            >
              <div className="relative h-32">
                <img
                  src={event.image}
                  alt={event.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-2 right-2 bg-gray-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                  COMPLETED
                </div>
              </div>
              <div className="p-3">
                <h4 className="font-bold text-gray-900 dark:text-white mb-1 line-clamp-1 text-sm">{event.title}</h4>
                <div className="flex items-center text-xs text-gray-600 dark:text-gray-400 mb-2">
                  <Calendar className="w-3 h-3 mr-1" />
                  {event.date}
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 dark:text-gray-400">Net Earnings</span>
                    <span className="font-bold text-green-600 dark:text-green-400">{event.netEarnings}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 dark:text-gray-400">Gross Revenue</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{event.grossRevenue}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Users className="w-3 h-3 mr-1" />
                      <span>Attendees</span>
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">{event.attendees}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Eye className="w-3 h-3 mr-1" />
                      <span>Total Views</span>
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">{event.views}</span>
                  </div>
                  <button className="w-full py-2 bg-[#27aae2]/10 dark:bg-[#27aae2]/20 text-[#27aae2] rounded-lg font-semibold hover:bg-[#27aae2]/20 dark:hover:bg-[#27aae2]/30 transition-colors text-xs">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Financial Note */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        <p className="text-sm text-blue-800 dark:text-blue-300">
          💰 <strong>Note:</strong> All earnings shown are net amounts after 7% platform deduction. Withdrawals are processed instantly via M-Pesa Daraja API split payments. Your funds dashboard is updated in real-time for 100% accuracy.
        </p>
      </div>
    </div>
  );
}
