import { Calendar, MapPin, Users, Heart, Share2 } from 'lucide-react';
import { useState } from 'react';

interface EventCardProps {
  id: string;
  title: string;
  image: string;
  date: string;
  time: string;
  location: string;
  attendees: number;
  category: string;
  price: string;
  onClick: (id: string) => void;
}

export default function EventCard({
  id,
  title,
  image,
  date,
  time,
  location,
  attendees,
  category,
  price,
  onClick
}: EventCardProps) {
  const [isFavorited, setIsFavorited] = useState(false);

  return (
    <div
      className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer border border-gray-100 relative"
      onClick={() => onClick(id)}
    >
      <div className="relative overflow-hidden aspect-[4/3]">
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 flex flex-col space-y-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsFavorited(!isFavorited);
            }}
            className="w-9 h-9 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white transition-colors shadow-lg"
          >
            <Heart className={`w-5 h-5 ${isFavorited ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
          </button>
        </div>
        <div className="absolute top-3 left-3">
          <span className="px-3 py-1 bg-blue-600 text-white text-xs font-semibold rounded-full">
            {category}
          </span>
        </div>
        {price === 'Free' ? (
          <div className="absolute bottom-3 left-3">
            <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full shadow-lg">
              FREE
            </span>
          </div>
        ) : (
          <div className="absolute bottom-3 left-3">
            <span className="px-3 py-1 bg-white/95 backdrop-blur-sm text-gray-900 text-xs font-bold rounded-full shadow-lg">
              {price}
            </span>
          </div>
        )}
      </div>

      <div className="p-5">
        <h3 className="font-bold text-lg text-gray-900 mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors">
          {title}
        </h3>

        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-blue-600" />
            <span className="font-medium">{date} • {time}</span>
          </div>
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-blue-600" />
            <span className="line-clamp-1">{location}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-blue-600" />
            <span>{attendees} attending</span>
          </div>
        </div>
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation();
          // Share functionality
          if (navigator.share) {
            navigator.share({
              title: title,
              text: `Check out this event: ${title}`,
              url: window.location.href
            });
          }
        }}
        className="absolute bottom-5 right-5 w-9 h-9 bg-blue-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-blue-700 shadow-lg z-10"
      >
        <Share2 className="w-4 h-4" />
      </button>
    </div>
  );
}
