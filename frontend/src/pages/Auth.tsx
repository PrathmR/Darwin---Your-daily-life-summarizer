// src/pages/Auth.tsx
import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft } from 'lucide-react';
import { ClipLoader } from "react-spinners";

declare global {
  interface Window {
    google?: any;
  }
}

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [googleLoaded, setGoogleLoaded] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
  const AUTH_BASE_URL = `${BACKEND_URL}/auth`;
  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

  const from = location.state?.from?.pathname || '/create-game';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLogin && !acceptTerms) {
      toast({ title: "Terms Required", description: "Please accept the Terms...", variant: "destructive" });
      return;
    }
    setIsLoading(true);
    try {
      const endpoint = isLogin ? '/login' : '/register';
      const response = await fetch(`${AUTH_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, ...(isLogin ? {} : { full_name: fullName }) }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        // handle particular cases
        if (!isLogin && response.status === 409 && data.detail === "Email is already registered.") {
          toast({ title: "Email Already Registered", description: "This email is already registered.", variant: "destructive" });
          setIsLogin(true); return;
        }
        if (isLogin && response.status === 403 && data.detail === "Email is not verified.") {
          toast({ title: "Email Not Verified", description: "Please verify your email first.", variant: "destructive" });
          return;
        }
        throw new Error(data.detail || 'Authentication failed');
      }
      if (isLogin) {
        toast({ title: "Success!", description: "You have been logged in successfully." });
        navigate(from, { replace: true });
      } else {
        toast({ title: "Almost there!", description: "Registration successful. Check your email." });
        setIsLogin(true); setEmail(''); setPassword(''); setFullName(''); setAcceptTerms(false);
      }
    } catch (error: any) {
      toast({ title: "Error", description: error?.message || "Authentication failed.", variant: "destructive" });
    } finally { setIsLoading(false); }
  };

  const goBack = () => navigate('/');

  const handleGoogleCallback = useCallback(async (response: any) => {
    try {
      if (!response?.credential) throw new Error('No credential returned from Google.');
      const res = await fetch(`${AUTH_BASE_URL}/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        credentials: "include",
        body: JSON.stringify({ credential: response.credential }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Google login failed.");
      toast({ title: "Signed in with Google", description: `Welcome ${data.email}` });
      navigate(from, { replace: true });
    } catch (err: any) {
      console.error("Google login error:", err);
      toast({ title: "Google login error", description: err?.message || "Unable to sign in with Google.", variant: "destructive" });
    }
  }, [AUTH_BASE_URL, toast, navigate, from]);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      console.warn("Google Client ID not configured");
      return;
    }

    const initializeGoogle = () => {
      try {
        if (!window.google?.accounts?.id) {
          console.warn("window.google.accounts.id not present yet");
          return;
        }
        // Useful debug: log origin and client id
        console.info("Initializing Google Identity:", { origin: window.location.origin, client_id: GOOGLE_CLIENT_ID });

        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleCallback,
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        setGoogleLoaded(true);

        const buttonDiv = document.getElementById('google-signin-button');
        if (buttonDiv) {
          window.google.accounts.id.renderButton(buttonDiv, {
            theme: "outline",
            size: "large",
            width: 384,
            text: "continue_with",
            shape: "pill",
          });
        }
      } catch (err) {
        console.error("Error initializing Google identity:", err);
      }
    };

    // If script already present and loaded
    if (window.google?.accounts?.id) {
      initializeGoogle();
      return;
    }

    const SRC = "https://accounts.google.com/gsi/client";
    const existingScript = document.querySelector<HTMLScriptElement>(`script[src="${SRC}"]`);
    let script: HTMLScriptElement | null = null;
    if (!existingScript) {
      script = document.createElement("script");
      script.src = SRC;
      script.async = true;
      script.defer = true;
      script.onload = () => {
        initializeGoogle();
      };
      script.onerror = () => {
        console.error("Failed to load Google Identity Services script");
        toast({ title: "Google Sign-In unavailable", description: "Could not load Google authentication.", variant: "destructive" });
      };
      document.body.appendChild(script);
    } else {
      // script exists — wait until window.google is available
      const check = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(check);
          initializeGoogle();
        }
      }, 100);
      // cleanup on unmount
      return () => clearInterval(check);
    }

    return () => {
      // remove script only if we created it (prevents removing other code's script)
      if (script) script.remove();
    };
  }, [GOOGLE_CLIENT_ID, handleGoogleCallback, toast]);

  return (
    <>
      <div className="min-h-screen flex flex-col overflow-hidden bg-grid" style={{ backgroundColor: "#F9F9F9" }}>
        <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl relative z-10">
          <button onClick={goBack} className="flex items-center text-gray-600 hover:text-black mb-6 transition-colors">
            <ArrowLeft size={20} className="mr-2" /><span>Back to Home</span>
          </button>

          <div className="flex mt-8 border p-1 border-gray-400 rounded-2xl bg-gradient-to-br from-white to-lime-100">
            <div className="w-full max-w-md rounded-2xl shadow-xl bg-white p-8 space-y-6 border border-gray-400">
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold tracking-tight text-gray-900">Welcome</h2>
                <p className="text-sm text-gray-500">{isLogin ? "Please enter your details to sign in" : "Create your account to get started"}</p>
              </div>

              <div className="flex justify-center">
                <div id="google-signin-button" className="w-full flex justify-center" style={{ minHeight: '40px' }} />
                {!googleLoaded && GOOGLE_CLIENT_ID && (
                  <div className="flex items-center justify-center w-full h-10"><ClipLoader size={20} /></div>
                )}
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-300" /></div>
                <div className="relative flex justify-center text-sm"><span className="bg-white px-2 text-gray-500">or</span></div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                  <input type="text" id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full Name" className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400" required />
                )}

                <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Your Email Address" className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400" required />

                <div className="relative">
                  <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400" required />
                </div>

                {isLogin && (
                  <div className="flex items-center justify-between text-sm">
                    <label className="flex items-center"><input type="checkbox" className="h-4 w-4 text-[#1a8b7e] rounded border-gray-300" /><span className="ml-2 text-gray-700">Remember me</span></label>
                  </div>
                )}

                {!isLogin && (
                  <div className="flex items-start text-sm text-gray-600">
                    <input id="terms" type="checkbox" checked={acceptTerms} onChange={(e) => setAcceptTerms(e.target.checked)} className="mt-1 h-4 w-4 text-[#1a8b7e] border-gray-300 rounded" />
                    <label htmlFor="terms" className="ml-2">By continuing, I accept the <Link to="/terms" className="text-[#1a8b7e] hover:underline">Terms of Service</Link> and <Link to="/privacy" className="text-[#1a8b7e] hover:underline">Privacy Policy</Link>.</label>
                  </div>
                )}

                <button type="submit" disabled={isLoading} className="w-full bg-gradient-to-r from-gray-800 to-black text-white py-3 rounded-lg font-semibold shadow-md hover:opacity-90 transition disabled:opacity-50">
                  {isLoading ? <ClipLoader color="#ffffff" size={20} /> : (isLogin ? "Sign In" : "Create Account")}
                </button>
              </form>

              <div className="text-center text-sm">
                <button onClick={() => setIsLogin(!isLogin)} className="text-[#1a8b7e] hover:underline">
                  {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
                </button>
              </div>
            </div>

            <div className="flex flex-col space-y-8 ml-4">
              <h1 className="text-5xl mt-28 font-bold tracking-tight ml-8 text-gray-700">Darwin</h1>
              <p className="text-lg text-gray-500 mr-8 ml-8">Darwin helps you summarize meetings and extract key points in seconds. Get an easy-to-read summary and full transcription instantly.</p>
            </div>
          </div>
        </div>
      </div>

      <style>{`.bg-grid { background-image: linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px); background-size: 30px 30px; }`}</style>
    </>
  );
};

export default Auth;








// -------------Claude code-------------

// // src/pages/Auth.tsx

// import { useState, useEffect, useCallback } from 'react';
// import { useNavigate, Link, useLocation } from 'react-router-dom';
// import { useToast } from "@/hooks/use-toast";
// import { ArrowLeft } from 'lucide-react';
// import { ClipLoader } from "react-spinners";

// declare global {
//   interface Window {
//     google?: any;
//   }
// }

// const Auth = () => {
//   const [isLogin, setIsLogin] = useState(true);
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [fullName, setFullName] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [acceptTerms, setAcceptTerms] = useState(false);
//   const [googleLoaded, setGoogleLoaded] = useState(false);
//   const { toast } = useToast();
//   const navigate = useNavigate();
//   const location = useLocation();

//   const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
//   const AUTH_BASE_URL = `${BACKEND_URL}/auth`;
//   const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

//   const from = location.state?.from?.pathname || '/create-game';

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();

//     if (!isLogin && !acceptTerms) {
//       toast({
//         title: "Terms Required",
//         description: "Please accept the Terms of Service and Privacy Policy to continue.",
//         variant: "destructive",
//       });
//       return;
//     }

//     setIsLoading(true);
//     try {
//       const endpoint = isLogin ? '/login' : '/register';

//       const response = await fetch(`${AUTH_BASE_URL}${endpoint}`, {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//           'Accept': 'application/json'
//         },
//         credentials: 'include',
//         body: JSON.stringify({
//           email,
//           password,
//           ...(isLogin ? {} : { full_name: fullName }),
//         }),
//       });

//       const data = await response.json().catch(() => ({}));

//       if (!response.ok) {
//         if (
//           !isLogin &&
//           response.status === 409 &&
//           data.detail === "Email is already registered."
//         ) {
//           toast({
//             title: "Email Already Registered",
//             description: "This email is already registered. Please try logging in instead.",
//             variant: "destructive",
//           });
//           setIsLogin(true);
//           return;
//         }

//         if (
//           isLogin &&
//           response.status === 403 &&
//           data.detail === "Email is not verified."
//         ) {
//           toast({
//             title: "Email Not Verified",
//             description: "Please verify your email first using the link we sent you.",
//             variant: "destructive",
//           });
//           return;
//         }

//         throw new Error(data.detail || 'Authentication failed');
//       }

//       if (isLogin) {
//         toast({
//           title: "Success!",
//           description: "You have been logged in successfully.",
//         });
//         navigate(from, { replace: true });
//       } else {
//         toast({
//           title: "Almost there!",
//           description: "Registration successful. Check your email to verify your account before logging in.",
//         });
//         setIsLogin(true);
//         setEmail('');
//         setPassword('');
//         setFullName('');
//         setAcceptTerms(false);
//       }
//     } catch (error: any) {
//       toast({
//         title: "Error",
//         description: error?.message || "Authentication failed. Please try again.",
//         variant: "destructive",
//       });
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const goBack = () => {
//     navigate('/');
//   };

//   // Google OAuth callback handler
//   const handleGoogleCallback = useCallback(async (response: any) => {
//     try {
//       const res = await fetch(`${AUTH_BASE_URL}/google`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Accept: "application/json",
//         },
//         credentials: "include",
//         body: JSON.stringify({
//           credential: response.credential,
//         }),
//       });

//       const data = await res.json().catch(() => ({}));

//       if (!res.ok) {
//         throw new Error(data.detail || "Google login failed.");
//       }

//       toast({
//         title: "Signed in with Google",
//         description: `Welcome ${data.email}`,
//       });

//       navigate(from, { replace: true });
//     } catch (err: any) {
//       console.error("Google login error:", err);
//       toast({
//         title: "Google login error",
//         description: err?.message || "Unable to sign in with Google. Please try again.",
//         variant: "destructive",
//       });
//     }
//   }, [AUTH_BASE_URL, toast, navigate, from]);

//   // Initialize Google Identity Services
//   useEffect(() => {
//     if (!GOOGLE_CLIENT_ID) {
//       console.warn("Google Client ID not configured");
//       return;
//     }

//     const initializeGoogle = () => {
//       if (window.google?.accounts?.id) {
//         window.google.accounts.id.initialize({
//           client_id: GOOGLE_CLIENT_ID,
//           callback: handleGoogleCallback,
//           auto_select: false,
//           cancel_on_tap_outside: true,
//         });
//         setGoogleLoaded(true);
        
//         // Render the Google button
//         const buttonDiv = document.getElementById('google-signin-button');
//         if (buttonDiv) {
//           window.google.accounts.id.renderButton(
//             buttonDiv,
//             { 
//               theme: "outline", 
//               size: "large",
//               width: 384,
//               text: "continue_with",
//               shape: "pill",
//             }
//           );
//         }
//       }
//     };

//     // Check if script already loaded
//     if (window.google?.accounts?.id) {
//       initializeGoogle();
//       return;
//     }

//     // Load the Google Identity Services script
//     const existingScript = document.querySelector<HTMLScriptElement>(
//       'script[src="https://accounts.google.com/gsi/client"]'
//     );

//     if (!existingScript) {
//       const script = document.createElement("script");
//       script.src = "https://accounts.google.com/gsi/client";
//       script.async = true;
//       script.defer = true;
//       script.onload = initializeGoogle;
//       script.onerror = () => {
//         console.error("Failed to load Google Identity Services");
//         toast({
//           title: "Google Sign-In unavailable",
//           description: "Could not load Google authentication. Please try email/password.",
//           variant: "destructive",
//         });
//       };
//       document.body.appendChild(script);

//       return () => {
//         script.remove();
//       };
//     } else {
//       // Script exists, wait for it to load
//       const checkGoogle = setInterval(() => {
//         if (window.google?.accounts?.id) {
//           clearInterval(checkGoogle);
//           initializeGoogle();
//         }
//       }, 100);

//       return () => clearInterval(checkGoogle);
//     }
//   }, [GOOGLE_CLIENT_ID, handleGoogleCallback, toast]);

//   return (
//     <>
//       <div className="min-h-screen flex flex-col overflow-hidden bg-grid" style={{ backgroundColor: "#F9F9F9" }}>
//         <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl relative z-10">
//           <button 
//             onClick={goBack}
//             className="flex items-center text-gray-600 hover:text-black mb-6 transition-colors"
//           >
//             <ArrowLeft size={20} className="mr-2" />
//             <span>Back to Home</span>
//           </button>

//           <div className="flex mt-8 border p-1 border-gray-400 rounded-2xl bg-gradient-to-br from-white to-lime-100">
//             <div className="w-full max-w-md rounded-2xl shadow-xl bg-white p-8 space-y-6 border border-gray-400">
//               <div className="text-center space-y-2">
//                 <h2 className="text-2xl font-bold tracking-tight text-gray-900">Welcome</h2>
//                 <p className="text-sm text-gray-500">
//                   {isLogin ? "Please enter your details to sign in" : "Create your account to get started"}
//                 </p>
//               </div>

//               {/* Google Sign-In Button Container */}
//               <div className="flex justify-center">
//                 <div 
//                   id="google-signin-button" 
//                   className="w-full flex justify-center"
//                   style={{ minHeight: '40px' }}
//                 />
//                 {!googleLoaded && GOOGLE_CLIENT_ID && (
//                   <div className="flex items-center justify-center w-full h-10">
//                     <ClipLoader size={20} />
//                   </div>
//                 )}
//               </div>

//               <div className="relative">
//                 <div className="absolute inset-0 flex items-center">
//                   <div className="w-full border-t border-gray-300" />
//                 </div>
//                 <div className="relative flex justify-center text-sm">
//                   <span className="bg-white px-2 text-gray-500">or</span>
//                 </div>
//               </div>

//               <form onSubmit={handleSubmit} className="space-y-4">
//                 {!isLogin && (
//                   <div>
//                     <input
//                       type="text"
//                       id="fullName"
//                       value={fullName}
//                       onChange={(e) => setFullName(e.target.value)}
//                       placeholder="Full Name"
//                       className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400"
//                       required
//                     />
//                   </div>
//                 )}

//                 <input
//                   type="email"
//                   id="email"
//                   value={email}
//                   onChange={(e) => setEmail(e.target.value)}
//                   placeholder="Your Email Address"
//                   className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400"
//                   required
//                 />

//                 <div className="relative">
//                   <input
//                     type="password"
//                     id="password"
//                     value={password}
//                     onChange={(e) => setPassword(e.target.value)}
//                     placeholder="Password"
//                     className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400"
//                     required
//                   />
//                 </div>

//                 {isLogin && (
//                   <div className="flex items-center justify-between text-sm">
//                     <label className="flex items-center">
//                       <input type="checkbox" className="h-4 w-4 text-[#1a8b7e] rounded border-gray-300" />
//                       <span className="ml-2 text-gray-700">Remember me</span>
//                     </label>
//                   </div>
//                 )}

//                 {!isLogin && (
//                   <div className="flex items-start text-sm text-gray-600">
//                     <input
//                       id="terms"
//                       type="checkbox"
//                       checked={acceptTerms}
//                       onChange={(e) => setAcceptTerms(e.target.checked)}
//                       className="mt-1 h-4 w-4 text-[#1a8b7e] border-gray-300 rounded"
//                     />
//                     <label htmlFor="terms" className="ml-2">
//                       By continuing, I accept the{' '}
//                       <Link to="/terms" className="text-[#1a8b7e] hover:underline">
//                         Terms of Service
//                       </Link>{' '}
//                       and{' '}
//                       <Link to="/privacy" className="text-[#1a8b7e] hover:underline">
//                         Privacy Policy
//                       </Link>
//                       .
//                     </label>
//                   </div>
//                 )}

//                 <button
//                   type="submit"
//                   disabled={isLoading}
//                   className="w-full bg-gradient-to-r from-gray-800 to-black text-white py-3 rounded-lg font-semibold shadow-md hover:opacity-90 transition disabled:opacity-50"
//                 >
//                   {isLoading ? (
//                     <ClipLoader color="#ffffff" size={20} />
//                   ) : isLogin ? (
//                     "Sign In"
//                   ) : (
//                     "Create Account"
//                   )}
//                 </button>
//               </form>

//               <div className="text-center text-sm">
//                 <button
//                   onClick={() => setIsLogin(!isLogin)}
//                   className="text-[#1a8b7e] hover:underline"
//                 >
//                   {isLogin
//                     ? "Don't have an account? Sign up"
//                     : "Already have an account? Sign in"}
//                 </button>
//               </div>
//             </div>

//             <div className="flex flex-col space-y-8 ml-4">
//               <h1 className="text-5xl mt-28 font-bold tracking-tight ml-8 text-gray-700">
//                 NeuroGEN
//               </h1>
//               <p className="text-lg text-gray-500 mr-8 ml-8">
//                 NeuroGEN streamlines research. Instead of clicking on individual
//                 links to find the right research paper to your interest, you get
//                 an easy-to-read summary & direct link. It also provides related
//                 questions that make it easy to explore more.
//               </p>
//             </div>
//           </div>
//         </div>
//       </div>

//       <style>{`
//         .bg-grid {
//           background-image: linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
//                             linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
//           background-size: 30px 30px;
//         }
//       `}</style>
//     </>
//   );
// };

// export default Auth;
















// -------------Anna's code & cursor refactoring-------------
// // src/pages/Auth.tsx

// import { useState, useEffect } from 'react';
// import { useNavigate, Link, useLocation } from 'react-router-dom';
// import { useToast } from "@/hooks/use-toast";
// import { ArrowLeft } from 'lucide-react';
// import { ClipLoader } from "react-spinners";

// declare global {
//   interface Window {
//     google?: any;
//   }
// }

// const Auth = () => {
//   const [isLogin, setIsLogin] = useState(true);
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [fullName, setFullName] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [acceptTerms, setAcceptTerms] = useState(false);
//   const { toast } = useToast();
//   const navigate = useNavigate();
//   const location = useLocation();

//   const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
//   const AUTH_BASE_URL = `${BACKEND_URL}/auth`;
//   const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

//   // Get the redirect path from location state or default to /create-game
//   const from = location.state?.from?.pathname || '/create-game';

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();

//     // ✅ Only require terms on sign-up, not login
//     if (!isLogin && !acceptTerms) {
//       toast({
//         title: "Terms Required",
//         description: "Please accept the Terms of Service and Privacy Policy to continue.",
//         variant: "destructive",
//       });
//       return;
//     }

//     setIsLoading(true);
//     try {
//       const endpoint = isLogin ? '/login' : '/register';

//       const response = await fetch(`${AUTH_BASE_URL}${endpoint}`, {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//           'Accept': 'application/json'
//         },
//         credentials: 'include', // ✅ important: send/receive cookies
//         body: JSON.stringify({
//           email,
//           password,
//           // backend ignores full_name, safe to send for now
//           ...(isLogin ? {} : { full_name: fullName }),
//         }),
//       });

//       const data = await response.json().catch(() => ({}));

//       if (!response.ok) {
//         // ✅ Handle specific backend errors

//         // Register: FastAPI returns 409 + "Email is already registered."
//         if (
//           !isLogin &&
//           response.status === 409 &&
//           data.detail === "Email is already registered."
//         ) {
//           toast({
//             title: "Email Already Registered",
//             description: "This email is already registered. Please try logging in instead.",
//             variant: "destructive",
//           });
//           setIsLogin(true);
//           return;
//         }

//         // Login: FastAPI returns 403 + "Email is not verified."
//         if (
//           isLogin &&
//           response.status === 403 &&
//           data.detail === "Email is not verified."
//         ) {
//           toast({
//             title: "Email Not Verified",
//             description: "Please verify your email first using the link we sent you.",
//             variant: "destructive",
//           });
//           return;
//         }

//         throw new Error(data.detail || 'Authentication failed');
//       }

//       if (isLogin) {
//         // ✅ Backend returns user info (UserPublic), tokens are in httpOnly cookies
//         // Optional: store minimal user info if you want:
//         // localStorage.setItem('user', JSON.stringify(data));

//         toast({
//           title: "Success!",
//           description: "You have been logged in successfully.",
//         });
//         navigate(from, { replace: true });
//       } else {
//         // ✅ After register, backend sends verification email
//         toast({
//           title: "Almost there!",
//           description: "Registration successful. Check your email to verify your account before logging in.",
//         });
//         setIsLogin(true);
//         setEmail('');
//         setPassword('');
//         setFullName('');
//         setAcceptTerms(false);
//       }
//     } catch (error: any) {
//       toast({
//         title: "Error",
//         description: error?.message || "Authentication failed. Please try again.",
//         variant: "destructive",
//       });
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const goBack = () => {
//     navigate('/');
//   };

//   const handleGoogleLogin = async () => {
//     if (!GOOGLE_CLIENT_ID) {
//       toast({
//         title: "Google Sign-In not configured",
//         description: "Missing VITE_GOOGLE_CLIENT_ID in frontend env.",
//         variant: "destructive",
//       });
//       return;
//     }

//     if (!window.google || !window.google.accounts || !window.google.accounts.id) {
//       toast({
//         title: "Google SDK not loaded",
//         description: "Please wait a moment and try again.",
//         variant: "destructive",
//       });
//       return;
//     }

//     // Initialize once per click (simple approach); you can optimize if needed
//     window.google.accounts.id.initialize({
//       client_id: GOOGLE_CLIENT_ID,
//       callback: async (response: any) => {
//         try {
//           const res = await fetch(`${AUTH_BASE_URL}/google`, {
//             method: "POST",
//             headers: {
//               "Content-Type": "application/json",
//               Accept: "application/json",
//             },
//             credentials: "include",
//             body: JSON.stringify({
//               credential: response.credential,
//             }),
//           });

//           const data = await res.json().catch(() => ({}));

//           if (!res.ok) {
//             throw new Error(data.detail || "Google login failed.");
//           }

//           // data is UserPublic; cookies are set httpOnly server-side
//           toast({
//             title: "Signed in with Google",
//             description: `Welcome ${data.email}`,
//           });

//           navigate(from, { replace: true });
//         } catch (err: any) {
//           toast({
//             title: "Google login error",
//             description:
//               err?.message || "Unable to sign in with Google. Please try again.",
//             variant: "destructive",
//           });
//         }
//       },
//     });

//     // Show Google account chooser
//     window.google.accounts.id.prompt();
//   };

//   // Load Google Identity script once
//   useEffect(() => {
//     if (!GOOGLE_CLIENT_ID) return;

//     const existingScript = document.querySelector<HTMLScriptElement>(
//       'script[src="https://accounts.google.com/gsi/client"]'
//     );
//     if (existingScript) return;

//     const script = document.createElement("script");
//     script.src = "https://accounts.google.com/gsi/client";
//     script.async = true;
//     script.defer = true;
//     document.body.appendChild(script);

//     return () => {
//       // optional cleanup
//       script.remove();
//     };
//   }, [GOOGLE_CLIENT_ID]);

//   return (
//     <>
//       <div className="min-h-screen flex flex-col overflow-hidden bg-grid" style={{ backgroundColor: "#F9F9F9" }}>
//         <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl relative z-10">
//           {/* Back button */}
//           <button 
//             onClick={goBack}
//             className="flex items-center text-gray-600 hover:text-black mb-6 transition-colors"
//           >
//             <ArrowLeft size={20} className="mr-2" />
//             <span>Back to Home</span>
//           </button>

//           <div className=" flex mt-8 border p-1 border-gray-400 rounded-2xl bg-gradient-to-br from-white to-lime-100">
//             <div className="w-full max-w-md rounded-2xl shadow-xl bg-white p-8 space-y-6 border border-gray-400">
//               <div className="text-center space-y-2">
//                 <h2 className="text-2xl font-bold tracking-tight text-gray-900">Welcome</h2>
//                 <p className="text-sm text-gray-500">
//                   {isLogin ? "Please enter your details to sign in" : "Create your account to get started"}
//                 </p>
//               </div>

//               {/* Social Buttons */}
//               <div className="flex justify-center space-x-4">
//                 <button
//                   type="button"
//                   onClick={handleGoogleLogin}
//                   className="flex items-center justify-center w-96 h-10 text-sm text-gray-500 rounded-full border border-gray-300 hover:bg-gray-50"
//                 >
//                   <img
//                     src="https://img.icons8.com/color/48/google-logo.png"
//                     alt="Google"
//                     className="w-5 h-5 mr-72"
//                   />
//                   Google
//                 </button>
//               </div>

//               <div className="relative">
//                 <div className="absolute inset-0 flex items-center">
//                   <div className="w-full border-t border-gray-300" />
//                 </div>
//                 <div className="relative flex justify-center text-sm">
//                   <span className="bg-white px-2 text-gray-500">or</span>
//                 </div>
//               </div>

//               <form onSubmit={handleSubmit} className="space-y-4">
//                 {!isLogin && (
//                   <div>
//                     <input
//                       type="text"
//                       id="fullName"
//                       value={fullName}
//                       onChange={(e) => setFullName(e.target.value)}
//                       placeholder="Full Name"
//                       className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400"
//                       required
//                     />
//                   </div>
//                 )}

//                 <input
//                   type="email"
//                   id="email"
//                   value={email}
//                   onChange={(e) => setEmail(e.target.value)}
//                   placeholder="Your Email Address"
//                   className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400"
//                   required
//                 />

//                 <div className="relative">
//                   <input
//                     type="password"
//                     id="password"
//                     value={password}
//                     onChange={(e) => setPassword(e.target.value)}
//                     placeholder="Password"
//                     className="w-full px-4 py-3 border text-slate-800 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] placeholder-gray-400"
//                     required
//                   />
//                 </div>

//                 {isLogin && (
//                   <div className="flex items-center justify-between text-sm">
//                     <label className="flex items-center">
//                       <input type="checkbox" className="h-4 w-4 text-[#1a8b7e] rounded border-gray-300" />
//                       <span className="ml-2 text-gray-700">Remember me</span>
//                     </label>
//                   </div>
//                 )}

//                 {!isLogin && (
//                   <div className="flex items-start text-sm text-gray-600">
//                     <input
//                       id="terms"
//                       type="checkbox"
//                       checked={acceptTerms}
//                       onChange={(e) => setAcceptTerms(e.target.checked)}
//                       className="mt-1 h-4 w-4 text-[#1a8b7e] border-gray-300 rounded"
//                     />
//                     <label htmlFor="terms" className="ml-2">
//                       By continuing, I accept the{' '}
//                       <Link to="/terms" className="text-[#1a8b7e] hover:underline">
//                         Terms of Service
//                       </Link>{' '}
//                       and{' '}
//                       <Link to="/privacy" className="text-[#1a8b7e] hover:underline">
//                         Privacy Policy
//                       </Link>
//                       .
//                     </label>
//                   </div>
//                 )}

//                 <button
//                   type="submit"
//                   disabled={isLoading}
//                   className="w-full bg-gradient-to-r from-gray-800 to-black text-white py-3 rounded-lg font-semibold shadow-md hover:opacity-90 transition"
//                 >
//                   {isLoading ? (
//                     <ClipLoader color="#ffffff" size={20} />
//                   ) : isLogin ? (
//                     "Sign In"
//                   ) : (
//                     "Create Account"
//                   )}
//                 </button>
//               </form>

//               <div className="text-center text-sm">
//                 <button
//                   onClick={() => setIsLogin(!isLogin)}
//                   className="text-[#1a8b7e] hover:underline"
//                 >
//                   {isLogin
//                     ? "Don't have an account? Sign up"
//                     : "Already have an account? Sign in"}
//                 </button>
//               </div>
//             </div>

//             <div className="flex flex-col space-y-8 ml-4">
//               <h1 className="text-5xl mt-28 font-bold tracking-tight ml-8 text-gray-700">
//                 NeuroGEN
//               </h1>
//               <p className="text-lg text-gray-500 mr-8 ml-8">
//                 NeuroGEN streamlines research. Instead of clicking on individual
//                 links to find the right research paper to your interest, you get
//                 an easy-to-read summary & direct link. It also provides related
//                 questions that make it easy to explore more.
//               </p>
//             </div>
//           </div>
//         </div>
//       </div>

//       <style>{`
//         .bg-grid {
//           background-image: linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
//                             linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
//           background-size: 30px 30px;
//         }
//       `}</style>
//     </>
//   );
// };

// export default Auth;
