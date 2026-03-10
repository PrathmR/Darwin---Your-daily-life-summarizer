import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { useEffect, useState } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const AUTH_BASE_URL = `${BACKEND_URL}/auth`;

const Header = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${AUTH_BASE_URL}/me`, {
          method: "GET",
          credentials: "include",
        });
        setIsAuthenticated(res.ok);
      } catch {
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = async () => {
    try {
      const res = await fetch(`${AUTH_BASE_URL}/logout`, {
        method: "POST",
        credentials: "include", // Important: send cookies
      });

      if (res.ok) {
        setIsAuthenticated(false);
        toast({
          title: "Logged out",
          description: "You have been successfully logged out.",
        });
        navigate('/');
      } else {
        throw new Error("Logout failed");
      }
    } catch (error) {
      // Even if backend call fails, clear local state
      setIsAuthenticated(false);
      toast({
        title: "Logged out",
        description: "You have been logged out.",
      });
      navigate('/');
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm border-b">
      {/* <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="text-xl font-bold text-gray-900"
            >
              NeuroGEN
            </button>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <button
                  onClick={() => navigate('/create-game')}
                  className="text-gray-600 hover:text-gray-900"
                >
                  Create Game
                </button>
                <button
                  onClick={handleLogout}
                  className="text-gray-600 hover:text-gray-900"
                >
                  Logout
                </button>
              </>
            ) : (
              <button
                onClick={() => navigate('/auth')}
                className="text-gray-600 hover:text-gray-900"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div> */}
    </header>
  );
};

export default Header;
