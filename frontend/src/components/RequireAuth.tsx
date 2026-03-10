// frontend/src/components/RequireAuth.tsx
import { useEffect, useState } from "react";
import { useLocation, Navigate } from "react-router-dom";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const AUTH_BASE_URL = `${BACKEND_URL}/auth`;

type RequireAuthProps = {
  children: React.ReactNode;
};

const RequireAuth = ({ children }: RequireAuthProps) => {
  const location = useLocation();
  const [status, setStatus] = useState<"checking" | "authed" | "unauth">(
    "checking"
  );

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${AUTH_BASE_URL}/me`, {
          method: "GET",
          credentials: "include", // use cookies
        });

        if (res.ok) {
          setStatus("authed");
        } else {
          setStatus("unauth");
        }
      } catch {
        setStatus("unauth");
      }
    };

    checkAuth();
  }, []);

  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Checking authentication...</p>
      </div>
    );
  }

  if (status === "unauth") {
    return (
      <Navigate
        to="/auth"
        state={{ from: location }}
        replace
      />
    );
  }

  // authed
  return <>{children}</>;
};

export default RequireAuth;
