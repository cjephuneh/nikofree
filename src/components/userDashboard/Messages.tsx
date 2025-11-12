import { Search, Send, MoreVertical, Phone, Video, Paperclip, Smile, Image as ImageIcon, MessageCircle } from 'lucide-react';
import { useState } from 'react';

export default function Messages() {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messageText, setMessageText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Messages feature coming soon - no API yet
  const conversations: any[] = [];

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeConversation = conversations.find(c => c.id === selectedConversation);

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-0.5 sm:mb-1">Messages</h1>
        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">Chat with event organizers and attendees</p>
      </div>

      {/* Empty State */}
      <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl border border-gray-200 dark:border-gray-700 p-12 text-center">
        <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
          <MessageCircle className="w-10 h-10 text-gray-400 dark:text-gray-500" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No messages yet</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
          Start a conversation with event organizers or other attendees
        </p>
        <button className="px-6 py-3 bg-[#27aae2] text-white rounded-lg font-semibold hover:bg-[#1e8bb8] transition-colors">
          Start New Conversation
        </button>
      </div>
    </div>
  );
}
