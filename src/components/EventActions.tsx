import { Calendar } from 'lucide-react';

export default function EventActions() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
      <button className="w-full py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl font-semibold text-gray-700 dark:text-gray-300 hover:border-[#27aae2] hover:text-[#27aae2] transition-all flex items-center justify-center space-x-2">
        <Calendar className="w-5 h-5" />
        <span>Add to Calendar</span>
      </button>
    </div>
  );
}
