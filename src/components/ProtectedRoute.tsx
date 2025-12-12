import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../services/authService';
import { getPartnerToken } from '../services/partnerService';

interface ProtectedRouteProps {
  children: React.ReactNode;
  type: 'user' | 'partner';
}

export default function ProtectedRoute({ children, type }: ProtectedRouteProps) {
  const navigate = useNavigate();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      if (type === 'user') {
        const authenticated = isAuthenticated();
        if (!authenticated) {
          navigate('/');
          return;
        }
        setIsAuthorized(true);
      } else if (type === 'partner') {
        const token = getPartnerToken();
        if (!token) {
          navigate('/');
          return;
        }
        setIsAuthorized(true);
      }
      setIsChecking(false);
    };

    checkAuth();
  }, [navigate, type]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#27aae2] mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return null;
  }

  return <>{children}</>;
}

