import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { ClipLoader } from "react-spinners";

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">(
    "idle"
  );
  const [message, setMessage] = useState<string>("");
  const { toast } = useToast();
  const navigate = useNavigate();

  const BACKEND_URL =
    import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
  const AUTH_BASE_URL = `${BACKEND_URL}/auth`;

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      toast({
        title: "Invalid link",
        description: "Verification token is missing from the URL.",
        variant: "destructive",
      });
      return;
    }

    const verify = async () => {
      setStatus("loading");
      try {
        const res = await fetch(
          `${AUTH_BASE_URL}/verify-email?token=${encodeURIComponent(token)}`,
          {
            method: "GET",
            credentials: "include",
          }
        );

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
          throw new Error(data.detail || "Verification failed.");
        }

        setStatus("success");
        setMessage(
          data.message || "Email verified successfully. You can now sign in."
        );

        toast({
          title: "Email verified",
          description: "You can now sign in with your account.",
        });

        // Optional: auto redirect after a short delay
        // setTimeout(() => navigate("/auth", { replace: true }), 2000);
      } catch (err: any) {
        setStatus("error");
        setMessage(
          err?.message ||
            "Verification failed. The link may be invalid or expired."
        );
        toast({
          title: "Verification failed",
          description:
            err?.message ||
            "The verification link may be invalid or expired.",
          variant: "destructive",
        });
      }
    };

    verify();
  }, [searchParams, AUTH_BASE_URL, toast, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-md p-8 border border-gray-200 text-center space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Email Verification</h1>

        {status === "loading" && (
          <div className="flex flex-col items-center space-y-3">
            <ClipLoader size={24} />
            <p className="text-gray-600">
              Verifying your email, please wait...
            </p>
          </div>
        )}

        {status === "success" && (
          <>
            <p className="text-green-700 font-medium">{message}</p>
            <button
              onClick={() => navigate("/auth")}
              className="mt-4 inline-flex items-center justify-center px-4 py-2 rounded-md bg-gray-900 text-white text-sm font-semibold hover:bg-black transition"
            >
              Go to Sign In
            </button>
          </>
        )}

        {status === "error" && (
          <>
            <p className="text-red-600 font-medium">{message}</p>
            <div className="mt-4 flex flex-col space-y-2">
              <button
                onClick={() => navigate("/auth")}
                className="inline-flex items-center justify-center px-4 py-2 rounded-md bg-gray-900 text-white text-sm font-semibold hover:bg-black transition"
              >
                Go to Sign In
              </button>
              <Link
                to="/"
                className="text-sm text-gray-500 hover:text-gray-800"
              >
                Return to Home
              </Link>
            </div>
          </>
        )}

        {status === "idle" && (
          <p className="text-gray-600">Preparing verification...</p>
        )}
      </div>
    </div>
  );
};

export default VerifyEmail;
