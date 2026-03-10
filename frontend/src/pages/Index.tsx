
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { LogOut, Upload, Brain, FileText, Mic, Sparkles, ArrowRight, ChevronRight, User, ChevronDown, LayoutDashboard } from 'lucide-react';
import FeatureCard from '@/components/FeatureCard';

const Index = () => {
  const [loaded, setLoaded] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [userEmail, setUserEmail] = useState<string>("");

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
  const AUTH_BASE_URL = `${BACKEND_URL}/auth`;

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${AUTH_BASE_URL}/me`, {
          method: "GET",
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          setUserEmail(data.email);
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch {
        setIsAuthenticated(false);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const handleLogout = async () => {
    try {
      const res = await fetch(`${AUTH_BASE_URL}/logout`, {
        method: "POST",
        credentials: "include",
      });
      if (res.ok) {
        setIsAuthenticated(false);
        toast({ title: "Logged out", description: "You have been successfully logged out." });
        navigate('/');
      } else { throw new Error("Logout failed"); }
    } catch {
      setIsAuthenticated(false);
      toast({ title: "Logged out", description: "You have been logged out." });
      navigate('/');
    }
  };

  const features = [
    {
      icon: <Mic className="w-6 h-6" />,
      title: "AI Transcription",
      description: "Upload audio or video files and get accurate, speaker-labeled transcripts instantly."
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "Smart Summarization",
      description: "Our powerful summarizer tool with customizable prompting extracts key decisions, action items, and discussion points into a structured summary."
    },
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Export Anywhere",
      description: "View your summary on-screen and export it as a professional PDF or Word document with one click."
    },
  ];

  const steps = [
    { number: "01", title: "Upload", description: "Drop your meeting recording — audio or video, any common format." },
    { number: "02", title: "AI Processes", description: "We transcribe, identify speakers, and extract insights with AI." },
    { number: "03", title: "Get Summary", description: "Review your polished summary and export as PDF or Word." },
  ];

  return (
    <div className="min-h-screen flex flex-col overflow-hidden bg-white text-black bg-grid">
      <style>{`
        .bg-grid {
          background-image: linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
          background-size: 30px 30px;
        }
      `}</style>

      {/* ─── NAVBAR (original style) ─── */}
      <div className="fixed my-4 md:px-32 px-8 w-screen z-[40] antialiased">
        <div className="relative">
          <div className="flex flex-col w-full backdrop-blur-2xl bg-white dark:bg-black items-center justify-between px-2 pt-2 pb-2 rounded-lg outline outline-1 outline-gray-200">
            <div className="flex flex-row w-full items-center justify-between">
              {/* Logo and Brand */}
              <div className="items-center flex flex-row gap-x-2 hover:cursor-pointer" role="button">
                <div className="w-6 h-6 relative">
                  <img
                    alt="Darwin Logo"
                    src="/t.png"
                    className="dark:block"
                    style={{
                      position: 'absolute',
                      height: '100%',
                      width: '100%',
                      inset: 0,
                      color: 'transparent',
                      objectFit: 'contain',
                    }}
                  />
                </div>
                <h3 onClick={() => navigate('/')}
                    className="hidden md:block text-xl font-semibold tracking-wide"> Darwin
                </h3>
              </div>

              {/* Desktop Nav */}
              <div className="hidden md:flex mr-2 flex-row items-center justify-between gap-x-4 font-mono font-medium">
                <a href="#features" className="text-muted-foreground hover:text-foreground transition-all duration-250">Features</a>
                <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-all duration-250">How It Works</a>
                <a href="#about" className="text-muted-foreground hover:text-foreground transition-all duration-250">About</a>

                {/* Login and Logout */}
                <div className="flex items-center space-x-4">
                  {isAuthenticated ? (
                    <div className="relative">
                      <button
                        onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                        className="flex items-center gap-2 text-muted-foreground hover:text-gray-900 bg-gray-50 hover:bg-gray-100 px-3 py-1.5 rounded-full border border-gray-200 transition-all duration-200"
                      >
                        <User className="w-4 h-4" />
                        <span className="text-sm">{userEmail.split('@')[0]}</span>
                        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${profileDropdownOpen ? 'rotate-180' : ''}`} />
                      </button>

                      {profileDropdownOpen && (
                        <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-xl shadow-lg py-2 flex flex-col z-50 overflow-hidden">
                          <div className="px-4 py-2 border-b border-gray-100 mb-1">
                            <p className="text-xs text-gray-500 font-medium">Signed in as</p>
                            <p className="text-sm font-semibold text-gray-900 truncate">{userEmail}</p>
                          </div>
                          
                          <button
                            onClick={() => { setProfileDropdownOpen(false); navigate('/create-game'); }}
                            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-emerald-700 hover:bg-emerald-50 transition-colors text-left"
                          >
                            <LayoutDashboard className="w-4 h-4" /> Dashboard
                          </button>
                          
                          <button
                            onClick={() => { setProfileDropdownOpen(false); handleLogout(); }}
                            className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors text-left"
                          >
                            <LogOut className="w-4 h-4" /> Logout
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => navigate('/auth')}
                      className="text-muted-foreground hover:text-gray-900"
                    >
                      Login
                    </button>
                  )}
                </div>
              </div>

              {/* Mobile Menu Icon */}
              <div className="md:hidden">
                <button
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="text-black dark:text-white focus:outline-none"
                >
                  {mobileMenuOpen ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                      className="lucide lucide-x mt-1">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                      className="lucide lucide-menu mt-1">
                      <line x1="4" x2="20" y1="12" y2="12"></line>
                      <line x1="4" x2="20" y1="6" y2="6"></line>
                      <line x1="4" x2="20" y1="18" y2="18"></line>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Mobile Dropdown Menu */}
            {mobileMenuOpen && (
              <div className="md:hidden flex flex-col font-mono font-medium gap-y-3 mt-2 w-full px-4 pb-3">
                <a href="#features" className="text-muted-foreground hover:text-foreground transition-all duration-250 text-left">Features</a>
                <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-all duration-250 text-left">How It Works</a>
                <a href="#about" className="text-muted-foreground hover:text-foreground transition-all duration-250 text-left">About</a>

                <div className="flex flex-col gap-y-2">
                  {isAuthenticated ? (
                    <>
                      <button
                        onClick={() => navigate('/create-game')}
                        className="text-muted-foreground hover:text-foreground text-left transition-all duration-250"
                      >
                        Summarize
                      </button>
                      <button
                        onClick={handleLogout}
                        className="text-muted-foreground hover:text-foreground flex items-center text-left transition-all duration-250"
                      >
                        Logout
                        <LogOut className="h-5 w-5 ml-2" />
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => navigate('/auth')}
                      className="text-muted-foreground hover:text-foreground text-left transition-all duration-250"
                    >
                      Login
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ─── HERO ─── */}
      <section className={`mt-60 pb-20 px-4 text-center transition-all duration-700 ${loaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-6 border border-emerald-200">
            <Sparkles className="w-3.5 h-3.5" /> Powered by advanced AI models
          </div>
          <h1 className="text-4xl md:text-6xl font-bold leading-tight tracking-tight mb-6">
            Turn Meetings into<br />
            <span className="text-emerald-600">Actionable Summaries</span>
          </h1>
          <p className="text-lg text-gray-500 max-w-xl mx-auto mb-10 leading-relaxed">
            Darwin uses AI to transcribe, analyze, and summarize your meeting recordings — giving you decisions, action items, and key insights in seconds.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={() => navigate(isAuthenticated ? '/create-game' : '/auth')}
              className="bg-emerald-600 text-white px-8 py-3 rounded-xl text-base font-semibold hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-200 flex items-center gap-2"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </button>
            <a
              href="#how-it-works"
              className="text-gray-500 hover:text-gray-900 px-6 py-3 rounded-xl text-base font-medium border border-gray-200 hover:border-gray-300 transition-all flex items-center gap-1"
            >
              See How It Works <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </section>

      {/* ─── FEATURES ─── */}
      <section id="features" className={`py-20 px-4 bg-gray-50 transition-all duration-700 delay-200 ${loaded ? 'opacity-100' : 'opacity-0'}`}>
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">Everything You Need</h2>
          <p className="text-gray-500 text-center max-w-lg mx-auto mb-14">From raw recordings to polished summaries — Darwin handles the entire pipeline.</p>
          <div className="grid md:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg hover:border-emerald-200 transition-all duration-300 group">
                <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-emerald-600 group-hover:text-white transition-colors duration-300">
                  {f.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── HOW IT WORKS ─── */}
      <section id="how-it-works" className={`py-20 px-4 transition-all duration-700 delay-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}>
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">How It Works</h2>
          <p className="text-gray-500 text-center max-w-lg mx-auto mb-14">Three simple steps to transform your meetings.</p>
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((s, i) => (
              <div key={i} className="text-center md:text-left">
                <div className="text-5xl font-black text-emerald-100 mb-3">{s.number}</div>
                <h3 className="text-xl font-bold mb-2">{s.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{s.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── ABOUT ─── */}
      <section id="about" className={`py-20 px-4 bg-gray-50 transition-all duration-700 delay-400 ${loaded ? 'opacity-100' : 'opacity-0'}`}>
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">About Darwin</h2>
          <p className="text-gray-500 leading-relaxed text-base mb-4">
            Darwin is an AI-powered meeting summarizer that transforms lengthy recordings into structured, actionable documents. Built with a modern tech stack, it automates transcription, extracts key decisions and action items, and lets you export professional reports.
          </p>
          <p className="text-gray-500 leading-relaxed text-base">
            Designed for teams, students, and professionals who attend multiple meetings daily but don't have time to re-watch recordings. Darwin turns hours of meetings into minutes of reading.
          </p>
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section className="py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold mb-4">Ready to summarize your next meeting?</h2>
          <p className="text-gray-500 mb-8">Upload a recording and get your summary in minutes.</p>
          <button
            onClick={() => navigate(isAuthenticated ? '/create-game' : '/auth')}
            className="bg-emerald-600 text-white px-8 py-3 rounded-xl text-base font-semibold hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-200 flex items-center gap-2 mx-auto"
          >
            <Upload className="w-4 h-4" /> Start Summarizing
          </button>
        </div>
      </section>

      {/* ─── FOOTER ─── */}
      <footer className="py-6 border-t bg-white border-gray-200">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 px-4">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 relative">
              <img alt="Darwin Logo" src="/t.png" style={{ height: '100%', width: '100%', objectFit: 'contain' }} />
            </div>
            <span className="font-semibold text-sm">Darwin</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="#features" className="hover:text-gray-900 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-gray-900 transition-colors">How It Works</a>
            <a href="#about" className="hover:text-gray-900 transition-colors">About</a>
          </div>
          <p className="text-xs text-gray-400">© 2025 Darwin. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;