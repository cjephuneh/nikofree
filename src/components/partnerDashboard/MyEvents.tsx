import { Calendar, MapPin, Users, Eye, Plus, Trash2, Edit } from 'lucide-react';
import { useState } from 'react';

interface MyEventsProps {
  onCreateEvent: () => void;
}

export default function MyEvents({ onCreateEvent }: MyEventsProps) {
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'ongoing' | 'past'>('all');
  const [events, setEvents] = useState([
    {
      id: 1,
      title: 'Summer Music Festival 2024',
      date: 'July 15, 2024',
      location: 'Central Park, Nairobi',
      ticketsSold: 450,
      totalTickets: 500,
      views: 2340,
      status: 'upcoming',
      image: 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400&h=250&fit=crop'
    },
    {
      id: 2,
      title: 'Tech Conference Kenya',
      date: 'August 20, 2024',
      location: 'KICC, Nairobi',
      ticketsSold: 380,
      totalTickets: 400,
      views: 1890,
      status: 'upcoming',
      image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400&h=250&fit=crop'
    },
    {
      id: 3,
      title: 'Food & Wine Expo',
      date: 'June 10, 2024',
      location: 'Carnivore Grounds',
      ticketsSold: 320,
      totalTickets: 350,
      views: 1560,
      status: 'ongoing',
      image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=250&fit=crop'
    },
    {
      id: 4,
      title: 'Comedy Night Live',
      date: 'May 25, 2024',
      location: 'Alliance Française',
      ticketsSold: 200,
      totalTickets: 200,
      views: 980,
      status: 'past',
      image: 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=400&h=250&fit=crop'
    },
    {
      id: 5,
      title: 'Art Exhibition 2024',
      date: 'September 5, 2024',
      location: 'National Museum',
      ticketsSold: 150,
      totalTickets: 300,
      views: 1120,
      status: 'upcoming',
      image: 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=400&h=250&fit=crop'
    }
  ]);

  const handleDeleteEvent = (eventId: number) => {
    if (window.confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
      setEvents(events.filter(event => event.id !== eventId));
    }
  };

  const handleEditEvent = (eventId: number) => {
    // In production, this would navigate to edit page or open edit modal
    alert(`Editing event ID: ${eventId}`);
  };

  const filteredEvents = filter === 'all' ? events : events.filter(e => e.status === filter);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">My Events</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage and track your events</p>
        </div>
        <button 
          onClick={onCreateEvent}
          className="flex items-center space-x-2 bg-[#27aae2] text-white px-6 py-3 rounded-xl font-medium hover:bg-[#1e8bc3] transition-all shadow-lg"
        >
          <Plus className="w-5 h-5" />
          <span>Create Event</span>
        </button>
      </div>

      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'all', label: 'All Events' },
          { id: 'upcoming', label: 'Upcoming' },
          { id: 'ongoing', label: 'Ongoing' },
          { id: 'past', label: 'Past' }
        ].map((item) => (
          <button
            key={item.id}
            onClick={() => setFilter(item.id as typeof filter)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filter === item.id
                ? 'bg-[#27aae2] text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Events Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredEvents.map((event) => (
          <div
            key={event.id}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-all"
          >
            <div className="relative h-40">
              <img
                src={event.image}
                alt={event.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  event.status === 'upcoming' ? 'bg-blue-500 text-white' :
                  event.status === 'ongoing' ? 'bg-green-500 text-white' :
                  'bg-gray-500 text-white'
                }`}>
                  {event.status.charAt(0).toUpperCase() + event.status.slice(1)}
                </span>
              </div>
            </div>

            <div className="p-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 line-clamp-2">
                {event.title}
              </h3>

              <div className="space-y-1.5 mb-3">
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <Calendar className="w-3.5 h-3.5" />
                  <span className="text-xs">{event.date}</span>
                </div>
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <MapPin className="w-3.5 h-3.5" />
                  <span className="text-xs truncate">{event.location}</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-600 dark:text-gray-400">Tickets</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {event.ticketsSold} / {event.totalTickets}
                  </span>
                </div>

                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div
                    className="bg-[#27aae2] h-1.5 rounded-full transition-all"
                    style={{ width: `${(event.ticketsSold / event.totalTickets) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between pt-1.5">
                  <div className="flex items-center space-x-3 text-xs text-gray-600 dark:text-gray-400">
                    <div className="flex items-center space-x-1">
                      <Users className="w-3.5 h-3.5" />
                      <span>{event.ticketsSold}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Eye className="w-3.5 h-3.5" />
                      <span>{event.views}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-4">
                    <button 
                      onClick={() => handleEditEvent(event.id)}
                      className="flex items-center space-x-1 text-[#27aae2] hover:text-[#1e8bc3] transition-colors"
                      title="Edit event"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => handleDeleteEvent(event.id)}
                      className="flex items-center space-x-1 text-red-500 hover:text-red-600 transition-colors"
                      title="Delete event"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredEvents.length === 0 && (
        <div className="text-center py-12">
          <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No {filter !== 'all' && filter} events found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {filter === 'all' 
              ? "You haven't created any events yet. Click 'Create Event' to get started!"
              : `You don't have any ${filter} events at the moment.`
            }
          </p>
        </div>
      )}
    </div>
  );
}
