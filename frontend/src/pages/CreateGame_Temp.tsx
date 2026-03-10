import { useState, useEffect, useRef } from 'react';
import { Share2, Download, Lock, Sparkles, ArrowLeft, ExternalLink, Info, Clipboard, FileText, BookOpen, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from 'react-router-dom';
import { ClipLoader } from "react-spinners";
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, Tooltip as RechartsTooltip } from 'recharts';
import { marked } from 'marked';
// import { Particles } from "@tsparticles/react";
// import { motion } from "framer-motion";

// TypeScript: declare SpeechRecognition on window for browser compatibility
// @ts-ignore
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

const researchCategories = [
  { id: 'medicine', name: 'Medical Research', icon: <span className="text-lg">🧬</span> },
  { id: 'ai', name: 'AI & ML', icon: <span className="text-lg">🤖</span> },
  { id: 'biology', name: 'Biology', icon: <span className="text-lg">🧫</span> },
  { id: 'physics', name: 'Physics', icon: <span className="text-lg">⚛️</span> },
  { id: 'climate', name: 'Climate Science', icon: <span className="text-lg">🌍</span> },
];

const trendingTopics = [
  "Artificial General Intelligence (AGI)",
  "Deep Learning in Medicine",
  "Quantum Computing",
  "Climate Change Models",
  "Protein Folding",
  "Reinforcement Learning",
  "Large Language Models",
  "Brain-Computer Interfaces",
  "CRISPR Gene Editing",
  "Autonomous Vehicles"
];

function getRecentQueries() {
  return JSON.parse(localStorage.getItem('recentResearchQueries') || '[]');
}
function addRecentQuery(query) {
  const recent = getRecentQueries();
  if (!recent.includes(query)) {
    recent.unshift(query);
    if (recent.length > 10) recent.pop();
    localStorage.setItem('recentResearchQueries', JSON.stringify(recent));
  }
}

function AutoSuggestSearchBar({ value, onChange, onSelect, loading, onMicClick, isListening, sttSupported }) {
  const [inputValue, setInputValue] = useState(value);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    setInputValue(value);
  }, [value]);

  useEffect(() => {
    const recents = getRecentQueries();
    setSuggestions([...recents, ...trendingTopics.filter(t => !recents.includes(t))]);
  }, [inputValue]);

  const filtered = suggestions.filter(
    s => s.toLowerCase().includes(inputValue.toLowerCase()) && s !== inputValue
  );

  function handleInputChange(e) {
    setInputValue(e.target.value);
    onChange(e.target.value);
    setShowSuggestions(true);
    setHighlightedIndex(-1);
  }

  function handleKeyDown(e) {
    if (!showSuggestions) return;
    if (e.key === 'ArrowDown') {
      setHighlightedIndex(idx => Math.min(idx + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      setHighlightedIndex(idx => Math.max(idx - 1, 0));
    } else if (e.key === 'Enter') {
      if (highlightedIndex >= 0 && filtered[highlightedIndex]) {
        onSelect(filtered[highlightedIndex]);
        setShowSuggestions(false);
      } else {
        onSelect(inputValue);
        setShowSuggestions(false);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  }

  function handleSuggestionClick(s) {
    onSelect(s);
    setShowSuggestions(false);
  }

  return (
    <div className="relative flex items-center">
      <input
        value={inputValue}
        onChange={handleInputChange}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 100)}
        onKeyDown={handleKeyDown}
        placeholder="Describe your research question..."
        className="w-full bg-[#F5F5F5] border border-gray-400 rounded-lg p-4 min-h-24 text-black focus:outline-none focus:ring-2 focus:ring-[#1a8b7e] resize-none"
        disabled={loading}
        style={{ fontSize: '1.1rem' }}
      />
      {sttSupported && (
        <button
          type="button"
          onClick={onMicClick}
          className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors ${isListening ? 'bg-[#1a8b7e] text-white' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'}`}
          aria-label={isListening ? 'Stop listening' : 'Start voice input'}
          tabIndex={-1}
        >
          {isListening ? <MicOff size={20} /> : <Mic size={20} />}
        </button>
      )}
      {showSuggestions && filtered.length > 0 && (
        <ul className="absolute left-0 right-0 bg-white border border-gray-300 rounded-lg mt-80 z-20 max-h-56 overflow-y-auto shadow-md">
          {filtered.map((item, idx) => (
            <li
              key={item}
              className={`px-4 py-2 cursor-pointer ${
                highlightedIndex === idx
                  ? 'bg-[#e6f4ef] text-black'
                  : 'text-gray-800 hover:bg-gray-100'
              }`}
              onMouseDown={() => handleSuggestionClick(item)}
              onMouseEnter={() => setHighlightedIndex(idx)}
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// function LoadingSpinner() {
//   return (
//     <motion.div
//       className="fixed inset-0 flex items-center justify-center bg-black/40 z-50"
//       initial={{ opacity: 0 }}
//       animate={{ opacity: 1 }}
//       exit={{ opacity: 0 }}
//     >
//       <motion.div
//         className="w-16 h-16 border-4 border-arcade-purple border-t-transparent rounded-full animate-spin"
//         animate={{ rotate: 360 }}
//         transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
//       />
//     </motion.div>
//   );
// }

function highlightTerms(text, terms) {
  if (!text) return '';
  let result = text;
  terms.forEach(term => {
    const regex = new RegExp(`(${term})`, 'gi');
    result = result.replace(regex, '<mark class="bg-[#e6f4ef] text-[#1a8b7e] font-semibold">$1</mark>');
  });
  return result;
}

function PaperDetailModal({ paper, open, onClose }) {
  if (!open || !paper) return null;
  function handleCopyBibtex() {
    if (paper.bibtex) {
      navigator.clipboard.writeText(paper.bibtex);
    }
  }
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-arcade-terminal rounded-xl p-4 sm:p-6 md:p-8 w-full max-w-lg mx-auto relative shadow-2xl border border-[#1a8b7e] overflow-y-auto max-h-[90vh] ">
        <button 
          onClick={onClose} 
          className="absolute top-3 right-3 text-gray-400 hover:text-white text-xl transition-colors"
          aria-label="Close modal"
        >
          ✕
        </button>
        <h2 className="text-xl sm:text-2xl font-bold text-[#3dbd90] mb-2 pr-8 break-words">
          {paper.title}
        </h2>
        {paper.authors && (
          <div className="text-sm text-gray-400 mb-2 break-words">
            {Array.isArray(paper.authors) ? paper.authors.join(", ") : paper.authors}
          </div>
        )}
        <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500 mb-2">
          {paper.year && (
            <span className="bg-gray-700 px-2 py-0.5 rounded whitespace-nowrap">
              {paper.year}
            </span>
          )}
          {paper.venue && (
            <span className="bg-gray-700 px-2 py-0.5 rounded break-words">
              {paper.venue}
            </span>
          )}
          {paper.citation_count && (
            <span className="bg-arcade-purple/20 text-[#3cc6b6] px-2 py-0.5 rounded whitespace-nowrap">
              {paper.citation_count} citations
            </span>
          )}
        </div>
        <div className="mb-4 text-gray-300 whitespace-pre-line leading-relaxed break-words">
          {paper.abstract || 'No abstract available.'}
        </div>
        {paper.url && (
          <a 
            href={paper.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="inline-flex items-center text-blue-400 hover:text-blue-300 underline text-sm mr-2 mb-2 transition-colors"
          >
            <ExternalLink size={16} className="mr-1" /> View Paper
          </a>
        )}
        {paper.source && (
          <span 
            className="inline-block bg-arcade-purple/20 text-[#3cc6b6]  px-2 py-1 rounded text-xs font-semibold mt-2 break-words" 
            title={paper.source}
          >
            Source: {paper.source}
          </span>
        )}
        {paper.bibtex && (
          <div className="mt-4">
            <div className="font-semibold text-gray-400 mb-1 flex items-center">
              BibTeX 
              <button 
                onClick={handleCopyBibtex} 
                className="ml-2 text-xs text-arcade-purple hover:text-arcade-purple/80 hover:underline flex items-center transition-colors"
              >
                <Clipboard size={14} className="mr-1" />Copy
              </button>
            </div>
            <pre className="bg-black/30 rounded p-2 text-xs text-gray-200 overflow-x-auto whitespace-pre-wrap break-words">
              {paper.bibtex}
            </pre>
          </div>
        )}
        {paper.citations && paper.citations.length > 0 && (
          <div className="mt-6">
            <div className="font-semibold text-gray-400 mb-2">Citations</div>
            <ul className="list-disc pl-5 text-xs text-gray-300 space-y-1 break-words">
              {paper.citations.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function ResearchGraph({ papers }) {
  // For demo, use citation_count and year as x/y
  const data = papers && papers.length > 0 ? papers.map((p, i) => ({
    x: Number(p.year) || 2020 + i,
    y: p.citation_count || 0,
    title: p.title,
    idx: i
  })) : [];
  return (
    <div className="bg-arcade-terminal/9 rounded-xl p-6 border border-gray-300 shadow-sm mb-8">
      <h3 className="text-lg font-bold mb-4 text-gray-600 flex items-center"><BookOpen size={18} className="mr-2" />Research Paper Graph</h3>
      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={250}>
          <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
            <XAxis dataKey="x" name="Year" tick={{ fill: '#3cc6b6' }} />
            <YAxis dataKey="y" name="Citations" tick={{ fill: '#3cc6b6' }} />
            <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} content={({ active, payload }) => active && payload && payload.length ? (
              <div className="bg-black/80 text-white p-2 rounded shadow">
                <div className="font-semibold text-[#3cc6b6] mb-1">{payload[0].payload.title}</div>
                <div className="text-xs">Year: {payload[0].payload.x}</div>
                <div className="text-xs">Citations: {payload[0].payload.y}</div>
              </div>
            ) : null} />
            <Scatter data={data} fill="#3cc6b6" />
          </ScatterChart>
        </ResponsiveContainer>
      ) : (
        <div className="text-gray-400 text-center py-8">No graph data available.</div>
      )}
    </div>
  );
}

const mockInsights = [
  "AGI research is rapidly evolving with increasing citation counts in recent years.",
  "Most top papers are published in high-impact venues like NeurIPS and Science Advances.",
  "Key trends: deep learning, reinforcement learning, and ethical considerations in AGI.",
  "Collaboration between neuroscience and AI is a growing theme."
];

const CreateGame = () => {
  const [researchQuery, setResearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [summary, setSummary] = useState("");
  const [papers, setPapers] = useState([]);
  const { toast } = useToast();
  const navigate = useNavigate();
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const keyTerms = ["Artificial General Intelligence", "AGI", "deep learning", "neural network", "reinforcement learning", "large language model", "protein folding", "climate", "autonomous", "brain-computer", "CRISPR"];
  const [isListening, setIsListening] = useState(false);
  const [sttSupported, setSttSupported] = useState(false);
  const recognitionRef = useRef<any>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);

  useEffect(() => {
    setSttSupported(!!SpeechRecognition);
    setTtsSupported(!!window.speechSynthesis);
  }, []);

  const handleCreate = async () => {
    if (!researchQuery.trim()) {
      toast({
        title: "Please describe your research query",
        variant: "destructive",
      });
      return;
    }
    try {
      setIsCreating(true);
      setSummary("");
      setPapers([]);
      addRecentQuery(researchQuery);
      const response = await fetch(`${BACKEND_URL}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: researchQuery }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSummary(data.summary || "No summary available.");
      setPapers(data.papers || []);
      toast({
        title: "Success!",
        description: "Your research has been analyzed.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to analyze research. Please try again.",
        variant: "destructive",
      });
      setSummary("Error analyzing research. Please try again.");
      setPapers([]);
    } finally {
      setIsCreating(false);
    }
  };

  const goBack = () => {
    navigate('/');
  };

  function handlePaperClick(paper) {
    setSelectedPaper(paper);
    setShowModal(true);
  }
  function handleModalClose() {
    setShowModal(false);
    setSelectedPaper(null);
  }
  function handleCopySummary() {
    navigator.clipboard.writeText(summary);
    toast({ title: "Copied!", description: "Summary copied to clipboard." });
  }
    function handleExportSummary() {
      const blob = new Blob([summary], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'research-summary.txt';
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: "Exported!", description: "Summary exported as text file." });
    }

    // --- Speech-to-Text logic ---
    const handleMicClick = () => {
      if (!sttSupported) return;
      if (!recognitionRef.current) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.onresult = (event: any) => {
          const transcript = Array.from(event.results)
            .map((result: any) => result[0].transcript)
            .join('');
          setResearchQuery(prev => prev ? prev + ' ' + transcript : transcript);
          setIsListening(false);
        };
        recognitionRef.current.onerror = () => {
          setIsListening(false);
        };
        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
      if (!isListening) {
        setIsListening(true);
        recognitionRef.current.start();
      } else {
        recognitionRef.current.stop();
        setIsListening(false);
      }
    };

    // --- Text-to-Speech logic ---
    const handleSpeakSummary = () => {
      if (!ttsSupported || !summary) return;
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
        return;
      }
      const utterance = new window.SpeechSynthesisUtterance(summary);
      utterance.lang = 'en-US';
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
    };
    useEffect(() => {
      // Clean up speech synthesis on unmount
      return () => {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (recognitionRef.current) recognitionRef.current.stop();
      };
    }, []);

    return (
      <>
        <div className="min-h-screen flex flex-col overflow-hidden bg-grid" style={{ backgroundColor: "#F9F9F9" }}>
          {/* Animated Particles Background */}
        {/* <Particles ... /> */}
        <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl relative z-10">
          {/* Back button */}
          <button 
            onClick={goBack}
            className="flex items-center text-gray-600 hover:text-black mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            <span>Back to home</span>
          </button>
  
          {/* Icon at the top */}
          <div className="w-full flex justify-center mb-6">
            {/* <div className="w-24 h-24 rounded-full bg-arcade-terminal flex items-center justify-center relative">
              <div className="absolute inset-0 rounded-full bg-arcade-purple opacity-20 blur-xl"></div>
              <div className="text-3xl">📚</div>
            </div> */}
          </div>
  
          {/* Main heading */}
          {/* <h1 className="text-4xl md:text-6xl font-bold text-[#2C2C2C] text-center mt-16 mb-16  tracking-tight"> */}
          <h1 className="text-4xl md:text-5xl font-mono font-bold leading-tight text-[#2C2C2C] text-center mt-16 mb-20  tracking-tight">
            Let's accelerate your research with AI.
          </h1>
  
          {/* Research query area */}
          <div className="backdrop-blur-sm rounded-xl p-6 border border-gray-300 shadow-xl max-w-4xl mx-auto mb-8" style={{ backgroundColor: '#f9f9f9' }}>
            <form onSubmit={e => { e.preventDefault(); handleCreate(); }}>
              <AutoSuggestSearchBar
                value={researchQuery}
                onChange={(val) => setResearchQuery(val)}
                onSelect={q => { setResearchQuery(q || ''); handleCreate(); }}
                loading={isCreating}
                onMicClick={handleMicClick}
                isListening={isListening}
                sttSupported={sttSupported}
              />
            </form>

            <div className="flex flex-wrap items-center justify-between mt-4">
              <div className="flex space-x-3">
                {/* <button className="p-2 text-gray-600 hover:text-black">
                  <Share2 size={20} />
                </button>
                <button className="p-2 text-gray-600 hover:text-black">
                  <Download size={20} />
                </button> */}
              </div>

              <div className="flex items-center space-x-3">
                {/* <div className="flex items-center px-3 py-1.5 text-sm border border-gray-400 rounded-lg bg-gray-100">
                  <Lock size={16} className="mr-2 text-gray-600" />
                  <span className="text-gray-700">Private</span>
                </div> */}
                <button 
                  onClick={handleCreate}
                  disabled={isCreating}
                  className="bg-[#1a8b7e] hover:bg-opacity-90  bg-[#c5eddf]/90 backdrop-blur-sm text-[#1a8b7e] hover:bg-[#1a8b7e]/90 tracking-wide hover:text-[#e6f4ef] border border-[#1a8b7e]/20 shadow-[0_4px_20px_rgba(26,139,126,0.15)] rounded-lg px-6 py-2 flex items-center font-medium disabled:opacity-70"
                >
                  <Sparkles size={18} className="mr-2" />
                  {isCreating ? "Analyzing..." : "Analyze"}
                </button>
              </div>
            </div>
          </div>

  
          {/* Loading Spinner Overlay */}
          {isCreating && (
            <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
              <ClipLoader color="#a78bfa" size={60} />
            </div>
          )}
  
          {showModal && <PaperDetailModal paper={selectedPaper} open={showModal} onClose={handleModalClose} />}
  
          {/* Research Results */}
          {(summary || papers.length > 0) && (
            <div className="max-w-4xl mx-auto space-y-8">
              {/*  Summary Section  */}
              <div className="backdrop-blur-sm rounded-xl p-6 border border-gray-300 shadow-xl max-w-4xl mx-auto mb-8" style={{ backgroundColor: '#f9f9f9' }}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-[#1a8b7e] flex items-center">
                    <Sparkles size={22} className="mr-2 " />Summary
                  </h2>
                  <div className="flex space-x-2">
                    {ttsSupported && (
                      <button
                        onClick={handleSpeakSummary}
                        className={`flex items-center px-3 py-1.5 text-xs rounded ${isSpeaking ? 'bg-[#1a8b7e] text-white' : 'bg-[#c5eddf] text-[#1a8b7e] hover:bg-[#1a8b7e] hover:text-white'}`}
                        aria-label={isSpeaking ? 'Stop reading summary' : 'Read summary aloud'}
                      >
                        {isSpeaking ? <VolumeX size={16} className="mr-1" /> : <Volume2 size={16} className="mr-1" />}Speak
                      </button>
                    )}
                    <button onClick={handleCopySummary} className="flex items-center px-3 py-1.5 text-xs rounded bg-[#c5eddf] text-[#1a8b7e] hover:bg-[#1a8b7e] hover:text-white">
                      <Clipboard size={16} className="mr-1" />Copy
                    </button>
                    <button onClick={handleExportSummary} className="flex items-center px-3 py-1.5 text-xs rounded bg-[#c5eddf] text-[#1a8b7e] hover:bg-[#1a8b7e] hover:text-white">
                      <FileText size={16} className="mr-1" />Export
                    </button>
                  </div>
                </div>
                {isCreating ? (
                  <div className="animate-pulse text-gray-500">Analyzing research...</div>
                ) : (
                  <div
                    className="compact-markdown prose prose-xl lg:prose-lg xl:prose-xl max-w-none text-gray-600 mb-4 whitespace-pre-line leading-relaxed dark:prose-invert"
                    style={{ lineHeight: 1.6 }}
                    dangerouslySetInnerHTML={{ __html: marked(highlightTerms(summary, keyTerms)) as string }}
                  />
                )}
              </div>
  
              {/* Insights Section  */}
              <div className="backdrop-blur-sm rounded-xl p-6 border border-gray-300 shadow-xl max-w-4xl mx-auto mb-8" style={{ backgroundColor: '#f9f9f9' }}>
                <h2 className="text-xl font-bold text-[#1a8b7e] flex items-center mb-4">
                  <Info size={20} className="mr-2" />Insights
                </h2>
                <ul className="list-disc pl-6 space-y-2 text-gray-600">
                  {mockInsights.map((insight, idx) => (
                    <li key={idx} className="leading-relaxed">{insight}</li>
                  ))}
                </ul>
              </div>
  
              {/* Analytics Section  */}
              <div className="backdrop-blur-sm rounded-xl p-6 border border-gray-300 shadow-xl max-w-4xl mx-auto mb-8" style={{ backgroundColor: '#f9f9f9' }}>
                <h2 className="text-xl font-bold text-[#1a8b7e] flex items-center mb-4">
                  <BookOpen size={20} className="mr-2" />Analytics
                </h2>
                <ResearchGraph papers={papers} />
                <div className="flex flex-wrap gap-4 mt-4">
                  {/* Metrics */}
                  <div className="bg-[#c5eddf]/90 backdrop-blur-sm text-[#1a8b7e] hover:bg-[#1a8b7e]/90 tracking-wide hover:text-[#e6f4ef] border border-[#1a8b7e]/20 shadow-[0_4px_20px_rgba(26,139,126,0.15)] rounded-lg p-4 flex-1 min-w-[180px] text-center">
                    <div className="text-2xl font-bold">{papers.length}</div>
                    <div className="text-xs mt-1">Papers Analyzed</div>
                  </div>
                  <div className="bg-[#c5eddf]/90 backdrop-blur-sm text-[#1a8b7e] hover:bg-[#1a8b7e]/90 tracking-wide hover:text-[#e6f4ef] border border-[#1a8b7e]/20 shadow-[0_4px_20px_rgba(26,139,126,0.15)] rounded-lg p-4 flex-1 min-w-[180px] text-center">
                    <div className="text-2xl font-bold">{papers.reduce((a, p) => a + (p.citation_count || 0), 0)}</div>
                    <div className="text-xs mt-1">Total Citations</div>
                  </div>
                  <div className="bg-[#c5eddf]/90 backdrop-blur-sm text-[#1a8b7e] hover:bg-[#1a8b7e]/90 tracking-wide hover:text-[#e6f4ef] border border-[#1a8b7e]/20 shadow-[0_4px_20px_rgba(26,139,126,0.15)] rounded-lg p-4 flex-1 min-w-[180px] text-center">
                    <div className="text-2xl font-bold">{[...new Set(papers.map(p => p.venue).filter(Boolean))].length}</div>
                    <div className="text-xs mt-1">Venues</div>
                  </div>
                </div>
              </div>

  
              {/*  Papers Section  */}
              <div className="backdrop-blur-sm rounded-xl p-6 border border-gray-300 shadow-xl max-w-4xl mx-auto mb-8" style={{ backgroundColor: '#f9f9f9' }}>
                <div className="border-t border-gray-300 my-6"></div>
                <h3 className="text-lg font-medium mb-4 text-gray-700 flex items-center">
                  <BookOpen size={18} className="mr-2" />Top Research Papers
                </h3>
                {isCreating ? (
                  <div className="animate-pulse text-gray-500">Loading papers...</div>
                ) : papers.length === 0 ? (
                  <div className="flex flex-col items-center text-gray-500 py-8">
                    <Info size={32} className="mb-2" />
                    <div>No papers found.</div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {papers.map((paper, idx) => (
                      <div key={idx} className="bg-gray-100 p-5 rounded-lg border border-gray-300 shadow hover:shadow-lg transition-shadow group relative flex flex-col">
                        <div className="flex items-center mb-2">
                          <span className="font-semibold text-[#1a8b7e] group-hover:underline text-base flex-1 cursor-pointer" onClick={() => handlePaperClick(paper)}>{paper.title || "Untitled"}</span>
                          {paper.url && (
                            <a href={paper.url} target="_blank" rel="noopener noreferrer" className="ml-2 text-[#1a8b7e] hover:underline text-xs flex items-center"><ExternalLink size={14} className="mr-1" />View</a>
                          )}
                        </div>
                        {paper.authors && (
                          <div className="text-xs text-gray-600 mb-1">{Array.isArray(paper.authors) ? paper.authors.join(", ") : paper.authors}</div>
                        )}
                        <div className="flex items-center gap-2 mb-1">
                          {paper.year && <span className="bg-gray-200 px-2 py-0.5 rounded text-xs">{paper.year}</span>}
                          {paper.venue && <span className="bg-gray-200 px-2 py-0.5 rounded text-xs">{paper.venue}</span>}
                          {paper.citation_count && <span className="bg-[#c5eddf] text-[#1a8b7e] px-2 py-0.5 rounded text-xs">{paper.citation_count} citations</span>}
                        </div>
                        <div className="text-gray-600 text-sm mt-2 leading-relaxed flex-1">{paper.abstract || "No abstract available."}</div>
                        <div className="flex items-center justify-between mt-4">
                          <span className="inline-block bg-[#c5eddf] text-[#1a8b7e] px-2 py-1 rounded text-xs font-semibold" title={paper.source}>{paper.source || 'Unknown Source'}</span>
                          <button onClick={() => handlePaperClick(paper)} className="text-xs text-[#1a8b7e] hover:underline flex items-center"><Info size={14} className="mr-1" />View Details</button>
                        </div>
                        {paper.citations && paper.citations.length > 0 && (
                          <div className="mt-3">
                            <div className="font-semibold text-gray-600 mb-1 text-xs">Citations</div>
                            <ul className="list-disc pl-5 text-xs text-gray-600 space-y-1">
                              {paper.citations.map((c, i) => <li key={i}>{c}</li>)}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
          )}
  
          {/* Research categories */}
          {/* <div className="flex flex-wrap justify-center gap-5 max-w-4xl mx-auto">
            {researchCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`inline-flex items-center justify-center whitespace-nowrap rounded-lg font-medium ring-offset-background transition-all duration-250 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 text-lg backdrop-blur-sm tracking-wide border shadow-[0_4px_20px_rgba(26,139,126,0.15)] space-x-2
                  ${
                    selectedCategory === category.id
                      ? 'bg-[#1a8b7e]/90 text-[#e6f4ef] border-[#1a8b7e]/20'
                      : 'bg-white text-[#1a8b7e]  border-[#1a8b7e]/20'
                  }`}
              >
                <span>{category.icon}</span>
                <span>{category.name}</span>
              </button>
            ))}
          </div> */}

        </div>
      </div>
  
      {/* <style jsx global>{`
        .bg-grid {
          background-image: 
            linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
          background-size: 30px 30px;
        }
      `}</style> */}
            <style>{`
        .compact-markdown {
          line-height: 1.5;
          font-size: 0.95rem;
        }

        .compact-markdown h1,
        .compact-markdown h2,
        .compact-markdown h3,
        .compact-markdown h4,
        .compact-markdown h5,
        .compact-markdown h6 {
          margin-top: 0.5em;
          margin-bottom: 0.2em;
          line-height: 1.4;
        }

        .compact-markdown p {
          margin-top: 0.2em;
          margin-bottom: 0.2em;
        }

        .compact-markdown ul,
        .compact-markdown ol {
          margin: 0.2em 0;
          padding-left: 1.25em;
        }

        .compact-markdown li {
          margin: 0.1em 0;
        }

        .compact-markdown blockquote {
          margin: 0.2em 0;
          padding-left: 0.8em;
          border-left: 2px solid #ccc;
          color: #666;
        }

        .compact-markdown pre {
          margin: 0.3em 0;
          padding: 0.6em;
          font-size: 0.9rem;
          background: #f5f5f5;
          border-radius: 4px;
          overflow-x: auto;
        }

        .compact-markdown code {
          background-color: #f5f5f5;
          padding: 0.2em 0.4em;
          border-radius: 3px;
          font-size: 0.9rem;
        }

        /* Optional: keep grid if used for background */
        .bg-grid {
          background-image: linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
          background-size: 30px 30px;
        }

        @media (max-width: 640px) {
          .compact-markdown {
            font-size: 0.9rem;
          }

          .compact-markdown h1,
          .compact-markdown h2,
          .compact-markdown h3,
          .compact-markdown h4,
          .compact-markdown h5,
          .compact-markdown h6 {
            margin-top: 0.4em;
            margin-bottom: 0.15em;
          }

          .compact-markdown ul,
          .compact-markdown ol {
            padding-left: 1em;
          }

          .compact-markdown pre {
            font-size: 0.85rem;
            padding: 0.5em;
          }
        }
      `}</style>
      <style>{`
        .compact-markdown {
          font-size: 0.92rem;
          line-height: 1.45;
        }

        .compact-markdown h1,
        .compact-markdown h2,
        .compact-markdown h3,
        .compact-markdown h4,
        .compact-markdown h5,
        .compact-markdown h6 {
          margin: 0.3em 0 0.15em 0;
          line-height: 1.3;
          font-weight: 600;
        }

        .compact-markdown p {
          margin: 0.1em 0;
        }

        .compact-markdown ul,
        .compact-markdown ol {
          margin: 0.1em 0;
          padding-left: 1.2em;
        }

        .compact-markdown li {
          margin: 0.05em 0;
        }

        .compact-markdown blockquote {
          margin: 0.2em 0;
          padding-left: 0.75em;
          border-left: 2px solid #ccc;
          color: #555;
          font-style: italic;
        }

        .compact-markdown code {
          background-color: #f0f0f0;
          padding: 0.15em 0.35em;
          font-size: 0.9rem;
          border-radius: 3px;
        }

        .compact-markdown pre {
          margin: 0.25em 0;
          padding: 0.5em 0.7em;
          background: #f5f5f5;
          font-size: 0.88rem;
          border-radius: 4px;
          overflow-x: auto;
        }

        .compact-markdown hr {
          margin: 0.4em 0;
          border: none;
          border-top: 1px solid #ddd;
        }

        @media (max-width: 640px) {
          .compact-markdown {
            font-size: 0.88rem;
          }

          .compact-markdown h1,
          .compact-markdown h2,
          .compact-markdown h3 {
            margin: 0.25em 0 0.1em 0;
          }

          .compact-markdown ul,
          .compact-markdown ol {
            padding-left: 1em;
          }

          .compact-markdown pre {
            font-size: 0.85rem;
          }
        }
      `}</style>

    </>
  );
  
};

export default CreateGame;
