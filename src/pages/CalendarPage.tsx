import React, { useState } from 'react';
import { MapPin, Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';

interface CalendarPageProps {
  onNavigate: (page: string) => void;
  onEventClick: (eventId: string) => void;
}

export default function CalendarPage({ onNavigate, onEventClick }: CalendarPageProps) {
  const [selectedLocation, setSelectedLocation] = useState('Nairobi, Kenya');
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
      date: 'Nov 15',
      time: '9:00 AM',
      location: 'KICC, Nairobi',
      attendees: 500,
      category: 'Technology',
      price: 'KES 2,000'
    },
    // Add more events as needed
  ];

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

        <div className="mb-8">
          <div className="flex items-center space-x-3 bg-white rounded-xl px-4 py-3 border border-gray-200 max-w-xs">
            <MapPin className="w-5 h-5 text-gray-400" />
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="flex-1 bg-transparent outline-none text-gray-900 cursor-pointer"
            >
              <option>Nairobi, Kenya</option>
              <option>Mombasa, Kenya</option>
              <option>Nakuru, Kenya</option>
              <option>Eldoret, Kenya</option>
              <option>Meru, Kenya</option>
            </select>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 mb-12">
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
                  aspect-square p-2 rounded-lg transition-all
                  ${!date ? 'invisible' : ''}
                  ${date && isToday(date) ? 'bg-blue-100 text-blue-600' : ''}
                  ${date && isSelectedDate(date) ? 'bg-blue-600 text-white' : ''}
                  ${date && !isToday(date) && !isSelectedDate(date) ? 'hover:bg-gray-100' : ''}
                `}
              >
                {date?.getDate()}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Events on {selectedDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => (
              <EventCard
                key={event.id}
                {...event}
                onClick={onEventClick}
              />
            ))}
            {events.length === 0 && (
              <div className="col-span-full text-center py-12">
                <p className="text-gray-600 text-lg">No events found on this date</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
