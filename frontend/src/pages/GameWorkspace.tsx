import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { 
  ArrowLeft, Settings, Code, Share, Maximize2, RefreshCw, Send 
} from 'lucide-react';

const GameWorkspace = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [prompt, setPrompt] = useState('');
  const [researchPrompt, setResearchPrompt] = useState('analyze recent papers on neural networks in medicine');
  const [aiResponse, setAiResponse] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [papers, setPapers] = useState([]);
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

  useEffect(() => {
    // Simulate AI generating a response after component mounts
    setAiResponse("I've analyzed papers based on your query: \"analyze recent papers on neural networks in medicine\". You can see the summary in the preview panel. Feel free to ask for any specific aspects or additional research!");
  }, []);

  const handleSearch = async (e) => {
    // Prevent form submission and navigation
    if (e) {
      e.preventDefault();
    }

    if (!prompt.trim()) {
      toast({
        title: "Error",
        description: "Please enter a search query",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      setSummary(""); // Clear previous summary
      setPapers([]); // Clear previous papers
      
      const response = await fetch(`${BACKEND_URL}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: prompt }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);

      if (!data || (!data.summary && !data.papers)) {
        throw new Error("Invalid response format from server");
      }

      setSummary(data.summary || "No summary available.");
      setPapers(data.papers || []);
    } catch (error) {
      console.error("Error fetching research data:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to fetch research data. Please try again.",
        variant: "destructive",
      });
      setSummary("Error fetching research data. Please try again.");
      setPapers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = () => {
    toast({
      title: "Share link copied!",
      description: "Research link has been copied to your clipboard.",
    });
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  }

  const handleRefresh = () => {
    toast({
      title: "Refreshing analysis...",
    });
    // Simulate refreshing the research preview
    setTimeout(() => {
      toast({
        title: "Analysis refreshed!",
      });
    }, 1000);
  }

  return (
    <div className="flex flex-col min-h-screen bg-arcade-dark items-center justify-start py-8">
      <div className="w-full max-w-2xl">
        {/* Search Bar */}
        <div className="p-4 border-b border-gray-800 mb-4">
          <div className="relative flex">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Type your research question..."
              className="flex-1 bg-black/40 text-white rounded-lg pl-4 pr-24 py-3 focus:outline-none focus:ring-1 focus:ring-arcade-purple"
              onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(e); }}
              disabled={loading}
            />
            <button
              onClick={(e) => handleSearch(e)}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-arcade-purple p-2 rounded-md text-white"
              disabled={loading}
            >
              {loading ? <span className="animate-spin">⏳</span> : "Search"}
            </button>
          </div>
        </div>
        {/* Results */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Research Summary</h2>
          <div className="mb-6">
            <h3 className="text-lg font-bold mb-2 text-gray-700">Summary</h3>
            {loading ? (
              <div className="animate-pulse text-gray-500">Loading summary...</div>
            ) : (
              <p className="text-gray-700 mb-4 whitespace-pre-line">{summary}</p>
            )}
          </div>
          <h3 className="text-lg font-medium mb-2 text-gray-700">Top 10 Research Papers</h3>
          {loading ? (
            <div className="animate-pulse text-gray-500">Loading papers...</div>
          ) : papers.length === 0 ? (
            <div className="text-gray-500">No papers found.</div>
          ) : (
            <ul className="space-y-4">
              {papers.map((paper, idx) => (
                <li key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <div className="font-semibold text-arcade-purple mb-1">{paper.title || "Untitled"}</div>
                  {paper.authors && (
                    <div className="text-xs text-gray-500 mb-1">{Array.isArray(paper.authors) ? paper.authors.join(", ") : paper.authors}</div>
                  )}
                  {paper.url && (
                    <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline text-xs mb-1 block">View Paper</a>
                  )}
                  <div className="text-gray-700 text-sm mt-2">{paper.abstract || "No abstract available."}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameWorkspace;
