import { useState } from 'react';
import LandingPage from './pages/LandingPage';
import EventDetailPage from './pages/EventDetailPage';
import UserDashboard from './pages/UserDashboard';
import PartnerDashboard from './pages/PartnerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import BecomePartner from './pages/BecomePartner';
import CreateEvent from './pages/CreateEvent';
import AboutUs from './pages/AboutUs';
import ThisWeekend from './pages/ThisWeekend';
import CalendarPage from './pages/CalendarPage';

type Page = 'landing' | 'event-detail' | 'user-dashboard' | 'partner-dashboard' | 'admin-dashboard' | 'become-partner' | 'create-event' | 'about' | 'calendar' | 'this-weekend';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [selectedEventId, setSelectedEventId] = useState<string>('1');

  const navigateToEventDetail = (eventId: string) => {
    setSelectedEventId(eventId);
    setCurrentPage('event-detail');
  };

  const navigateTo = (page: string) => {
    setCurrentPage(page as Page);
  };

  return (
    <div className="min-h-screen bg-white">
      {currentPage === 'landing' && (
        <LandingPage
          onNavigate={navigateTo}
          onEventClick={navigateToEventDetail}
        />
      )}
      {currentPage === 'event-detail' && (
        <EventDetailPage
          eventId={selectedEventId}
          onNavigate={navigateTo}
        />
      )}
      {currentPage === 'user-dashboard' && (
        <UserDashboard onNavigate={navigateTo} />
      )}
      {currentPage === 'partner-dashboard' && (
        <PartnerDashboard onNavigate={navigateTo} />
      )}
      {currentPage === 'admin-dashboard' && (
        <AdminDashboard onNavigate={navigateTo} />
      )}
      {currentPage === 'become-partner' && (
        <BecomePartner onNavigate={navigateTo} />
      )}
      {currentPage === 'create-event' && (
        <CreateEvent onNavigate={navigateTo} />
      )}
      {currentPage === 'about' && (
        <AboutUs onNavigate={navigateTo} />
      )}
      {currentPage === 'this-weekend' && (
        <ThisWeekend onNavigate={navigateTo} onEventClick={navigateToEventDetail} />
      )}
      {currentPage === 'calendar' && (
        <CalendarPage onNavigate={navigateTo} onEventClick={navigateToEventDetail} />
      )}
    </div>
  );
}

export default App;
