import React, { useState } from 'react';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';

interface CalendarPageProps {
  onNavigate: (page: string) => void;
  onEventClick: (eventId: string) => void;
}

export default function CalendarPage({ onNavigate, onEventClick }: CalendarPageProps) {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedMonth, setSelectedMonth] = useState(new Date());

  const daysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const startOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const generateCalendarDays = () => {
    const days = [];
    const totalDays = daysInMonth(selectedMonth);
    const startDay = startOfMonth(selectedMonth);

    // Add empty cells for days before the start of the month
    for (let i = 0; i < startDay; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let i = 1; i <= totalDays; i++) {
      days.push(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth(), i));
    }

    return days;
  };

  const nextMonth = () => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1));
  };

  const prevMonth = () => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1));
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isSelectedDate = (date: Date) => {
    return date.toDateString() === selectedDate.toDateString();
  };

  // Sample events data
  const events = [
    {
      id: '1',
      title: 'Tech Conference',
      image: 'https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Nov 15, 2025',
      time: '9:00 AM',
      location: 'KICC, Nairobi',
      attendees: 500,
      category: 'Technology',
      price: 'KES 2,000'
    },
    {
      id: '2',
      title: 'Music Festival',
      image: 'https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Nov 15, 2025',
      time: '6:00 PM',
      location: 'Uhuru Park, Nairobi',
      attendees: 1000,
      category: 'Music',
      price: 'KES 1,500'
    },
    {
      id: '3',
      title: 'Fitness Bootcamp',
      image: 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Nov 18, 2025',
      time: '7:00 AM',
      location: 'Karura Forest, Nairobi',
      attendees: 50,
      category: 'Sports & Fitness',
      price: 'KES 500'
    },
    {
      id: '4',
      title: 'Art Exhibition',
      image: 'https://images.pexels.com/photos/1839919/pexels-photo-1839919.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Nov 20, 2025',
      time: '10:00 AM',
      location: 'National Museum, Nairobi',
      attendees: 200,
      category: 'Arts & Culture',
      price: 'KES 300'
    },
    {
      id: '5',
      title: 'Startup Pitch Night',
      image: 'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Nov 22, 2025',
      time: '5:00 PM',
      location: 'iHub, Nairobi',
      attendees: 150,
      category: 'Business',
      price: 'Free'
    },
    {
      id: '6',
      title: 'Food Festival',
      image: 'https://images.pexels.com/photos/1267320/pexels-photo-1267320.jpeg?auto=compress&cs=tinysrgb&w=800',
      date: 'Nov 25, 2025',
      time: '12:00 PM',
      location: 'Two Rivers Mall, Nairobi',
      attendees: 800,
      category: 'Food & Drink',
      price: 'KES 1,000'
    },
  ];

  const getEventsForDate = (date: Date) => {
    return events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  const hasEvents = (date: Date) => {
    return getEventsForDate(date).length > 0;
  };

  const selectedDateEvents = getEventsForDate(selectedDate);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Navbar onNavigate={onNavigate} currentPage="calendar" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 bg-blue-100 px-4 py-2 rounded-full mb-6">
            <CalendarIcon className="w-4 h-4 text-blue-600" />
            <span className="text-blue-600 text-sm font-medium">Event Calendar</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Browse Events by Date
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Find events on specific dates and plan your schedule
          </p>
        </div>

        
        <div className="bg-white rounded-2xl border p-6 mb-12">
          <div className="flex justify-between items-center mb-6">
            <button
              onClick={prevMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-semibold">{formatDate(selectedMonth)}</h2>
            <button
              onClick={nextMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-7 gap-2 mb-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="text-center text-sm font-medium text-gray-600 py-2">
                {day}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-2">
            {generateCalendarDays().map((date, index) => (
              <button
                key={index}
                onClick={() => date && setSelectedDate(date)}
                className={`
                  aspect-square p-1 rounded-lg transition-all relative flex flex-col items-start
                  ${!date ? 'invisible' : ''}
                  ${date && isToday(date) ? 'bg-blue-100 text-blue-600' : ''}
                  ${date && isSelectedDate(date) ? 'bg-blue-600 text-white' : ''}
                  ${date && !isToday(date) && !isSelectedDate(date) ? 'hover:bg-gray-100' : ''}
                `}
              >
                <span className="text-sm font-medium mb-0.5">{date?.getDate()}</span>
                {date && hasEvents(date) && (
                  <div className="w-full space-y-0.5 overflow-hidden">
                    {getEventsForDate(date).slice(0, 2).map((event, i) => (
                      <div
                        key={i}
                        className={`text-[8px] leading-tight truncate w-full px-0.5 py-0.5 rounded ${
                          isSelectedDate(date) 
                            ? 'bg-white/20 text-white' 
                            : 'bg-blue-100 text-blue-700'
                        }`}
                        title={event.title}
                      >
                        {event.title}
                      </div>
                    ))}
                    {getEventsForDate(date).length > 2 && (
                      <div
                        className={`text-[8px] text-center ${
                          isSelectedDate(date) ? 'text-white/70' : 'text-gray-500'
                        }`}
                      >
                        +{getEventsForDate(date).length - 2}
                      </div>
                    )}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Events on {selectedDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            {selectedDateEvents.length > 0 && (
              <span className="ml-2 text-blue-600">({selectedDateEvents.length})</span>
            )}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {selectedDateEvents.map((event) => (
              <EventCard
                key={event.id}
                {...event}
                onClick={onEventClick}
              />
            ))}
            {selectedDateEvents.length === 0 && (
              <div className="col-span-full text-center py-12">
                <CalendarIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600 text-lg">No events found on this date</p>
                <p className="text-gray-500 text-sm mt-2">Try selecting another date</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
