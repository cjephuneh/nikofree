import React, { useState } from 'react';
import { MapPin, Calendar, Filter } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';

interface ThisWeekendProps {
  onNavigate: (page: string) => void;
  onEventClick: (eventId: string) => void;
}

export default function ThisWeekend({ onNavigate, onEventClick }: ThisWeekendProps) {
  const [selectedLocation, setSelectedLocation] = useState('Nairobi, Kenya');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const weekendEvents = [
    {
      id: '1',
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
      id: '2',
      title: 'Jazz Night Live',
      image: 'https://images.pexels.com/photos/1481308/pexels-photo-1481308.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Sat, Nov 2',
      time: '8:00 PM',
      location: 'Alliance Française',
      attendees: 189,
      category: 'Music',
      price: 'KES 800'
    },
    {
      id: '3',
      title: 'Morning Yoga in the Park',
      image: 'https://images.pexels.com/photos/3822647/pexels-photo-3822647.jpeg?auto=compress&cs=tinysrgb&w=600',
      date: 'Sun, Nov 3',
      time: '6:00 AM',
      location: 'Karura Forest',
      attendees: 45,
      category: 'Fitness',
      price: 'Free'
    }
    // Add more weekend events as needed
  ];

  const categories = ['All', 'Music', 'Culture', 'Sports', 'Food', 'Technology', 'Fitness'];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Navbar onNavigate={onNavigate} currentPage="this-weekend" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 bg-blue-100 px-4 py-2 rounded-full mb-6">
            <Calendar className="w-4 h-4 text-blue-600" />
            <span className="text-blue-600 text-sm font-medium">This Weekend</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Weekend Events Near You
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover exciting events happening this weekend in your area
          </p>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 flex items-center space-x-3 bg-white rounded-xl px-4 py-3 border border-gray-200">
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
          <div className="flex items-center space-x-3 bg-white rounded-xl px-4 py-3 border border-gray-200">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent outline-none text-gray-900 cursor-pointer min-w-[120px]"
            >
              {categories.map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {weekendEvents.map((event) => (
            <EventCard
              key={event.id}
              {...event}
              onClick={onEventClick}
            />
          ))}
        </div>

        {weekendEvents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No events found for this weekend</p>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
