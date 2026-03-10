import { Navigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const AUTH_BASE_URL = `${BACKEND_URL}/auth`;

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const location = useLocation();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${AUTH_BASE_URL}/me`, {
          method: "GET",
          credentials: "include", // use cookies
        });

        setIsAuthenticated(res.ok);
      } catch {
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    // Still checking
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Checking authentication...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to auth page but save the attempted URL
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 