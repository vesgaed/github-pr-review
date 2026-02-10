import { useState, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Github,
  Search,
  GitPullRequest,
  Clock,
  ExternalLink,
  Loader2,
  ChevronRight,
  ShieldAlert,
  BarChart2,
  Bot,
  ChevronLeft,
  Layout,
  Filter,
  User
} from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
import { UserRepositories } from './components/UserRepositories';
import { StatsDashboard } from './components/StatsDashboard';

// Helper for Tailwind classes
function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

interface PullRequest {
  number: number;
  title: string;
  author: string;
  author_avatar: string;
  html_url: string;
  labels: string[];
  is_draft: boolean;
  state: string;
  created_at: string;
  updated_at: string;
  body: string;
}

interface ApiResponse {
  items: PullRequest[];
  pages_fetched: number;
  from_cache: boolean;
  repository: string;
}

const ITEMS_PER_PAGE = 8; // Slightly less for sidebar layout

export default function App() {
  const [repository, setRepository] = useState('vercel/next.js');
  const [token, setToken] = useState('');
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxPages, setMaxPages] = useState(3);
  const [bypassCache, setBypassCache] = useState(false);

  // Client-side Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPR, setSelectedPR] = useState<PullRequest | null>(null);

  // AI Summary State
  const [summaries, setSummaries] = useState<Record<number, string>>({});
  const [loadingSummary, setLoadingSummary] = useState<number | null>(null);

  const fetchData = async (repoName: string) => {
    setLoading(true);
    setError(null);
    setData(null);
    setSelectedPR(null);
    setCurrentPage(1); // Reset to first page on new fetch

    try {
      const params = new URLSearchParams({
        repository: repoName,
        max_pages: maxPages.toString(),
        bypass_cache: bypassCache.toString(),
      });
      if (token) params.append('token', token);

      const response = await fetch(`/api/pull-requests?${params.toString()}`);

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || `HTTP Error ${response.status}`);
      }

      const result = await response.json();
      setData(result);
      if (result.items.length > 0) {
        setSelectedPR(result.items[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleFetch = (e?: React.FormEvent) => {
    e?.preventDefault();
    fetchData(repository);
  };

  const handleSelectRepo = (repoName: string) => {
    setRepository(repoName);
    fetchData(repoName);
  };

  const fetchSummary = async (prNumber: number) => {
    if (summaries[prNumber]) return; // Already fetched
    setLoadingSummary(prNumber);
    try {
      const params = new URLSearchParams({ repository });
      if (token) params.append('token', token);

      const res = await fetch(`/api/pr/${prNumber}/summary?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch summary');

      const data = await res.json();
      setSummaries(prev => ({ ...prev, [prNumber]: data.summary }));
    } catch (error) {
      console.error(error);
      setSummaries(prev => ({ ...prev, [prNumber]: 'Failed to generate summary. Is GEMINI_API_KEY set in backend .env?' }));
    } finally {
      setLoadingSummary(null);
    }
  };

  const getStatusColor = (isDraft: boolean) => {
    if (isDraft) return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    return 'bg-green-500/10 text-green-500 border-green-500/20';
  };

  // Pagination Logic
  const totalItems = data?.items.length || 0;
  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);
  const currentItems = data?.items.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  ) || [];

  return (
    <div className="h-screen bg-neutral-950 text-neutral-100 font-sans selection:bg-blue-500/30 flex flex-col overflow-hidden">
      {/* Header - Compact */}
      <header className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-xl shrink-0 z-50">
        <div className="max-w-[1920px] mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-neutral-800 rounded-lg">
              <Github className="w-5 h-5 text-white" />
            </div>
            <h1 className="font-bold text-base tracking-tight flex items-center gap-2">
              PR Status <span className="text-neutral-500 font-medium">Explorer</span>
              <span className="px-1.5 py-0.5 rounded-md bg-purple-500/10 text-purple-400 text-[10px] font-bold border border-purple-500/20">v1.2</span>
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick Search Bar */}
            <form onSubmit={handleFetch} className="relative group w-96 hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500 group-focus-within:text-blue-400 transition-colors" />
              <input
                type="text"
                value={repository}
                onChange={(e) => setRepository(e.target.value)}
                placeholder="Search repository (owner/name)..."
                className="w-full bg-neutral-900 border border-neutral-800 rounded-full pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder:text-neutral-600"
              />
            </form>

            <div className="h-4 w-px bg-neutral-800"></div>

            <div className="flex items-center gap-3 text-xs text-neutral-400">
              <a href="https://github.com/settings/tokens" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-1">
                <ExternalLink className="w-3 h-3" /> Token
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Split View */}
      <div className="flex-1 flex overflow-hidden">

        {/* Left Sidebar - List */}
        <aside className="w-[450px] border-r border-neutral-800 bg-neutral-900/20 flex flex-col shrink-0">

          {/* Controls */}
          <div className="p-4 border-b border-neutral-800 space-y-3">
            <div className="flex gap-2">
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="GitHub Token (Optional)"
                className="flex-1 bg-neutral-900 border border-neutral-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-blue-500/50"
              />
              <button
                onClick={(e) => handleFetch(e)}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Fetch'}
              </button>
            </div>

            <div className="flex items-center justify-between text-xs text-neutral-400">
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input type="checkbox" checked={bypassCache} onChange={e => setBypassCache(e.target.checked)} className="rounded border-neutral-700 bg-neutral-900 text-blue-600 focus:ring-0" />
                  No Cache
                </label>
                <span className="text-neutral-600">|</span>
                <span className="">Max Pages: {maxPages}</span>
              </div>
              {data && (
                <span className="text-neutral-300 font-medium">{data.items.length} PRs</span>
              )}
            </div>
          </div>

          {/* PR List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
            {error && (
              <div className="p-4 bg-red-500/10 text-red-400 text-xs rounded-lg m-2 border border-red-500/20">
                {error}
              </div>
            )}

            {!data && !loading && (
              <div className="h-full flex flex-col items-center justify-center text-neutral-500 gap-2 p-8 text-center">
                <GitPullRequest className="w-8 h-8 opacity-20" />
                <p className="text-sm">Select a repository to view Pull Requests</p>
              </div>
            )}

            {loading && (
              <div className="flex justify-center p-8">
                <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
              </div>
            )}

            {currentItems.map((pr) => (
              <div
                key={pr.number}
                onClick={() => setSelectedPR(pr)}
                className={cn(
                  "group p-3 rounded-lg border cursor-pointer transition-all hover:bg-neutral-800/50",
                  selectedPR?.number === pr.number
                    ? "bg-blue-500/10 border-blue-500/30 shadow-[0_0_15px_-5px_rgba(59,130,246,0.3)]"
                    : "bg-neutral-900/40 border-neutral-800 hover:border-neutral-700"
                )}
              >
                <div className="flex items-start gap-3">
                  <img src={pr.author_avatar} alt={pr.author} className="w-8 h-8 rounded-full border border-neutral-700/50" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className={cn("text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase", getStatusColor(pr.is_draft))}>
                        #{pr.number}
                      </span>
                      <span className="text-[10px] text-neutral-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(pr.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className={cn("text-sm font-medium truncate leading-snug mb-1", selectedPR?.number === pr.number ? "text-blue-200" : "text-neutral-300")}>
                      {pr.title}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-neutral-500">@{pr.author}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Footer */}
          {totalPages > 1 && (
            <div className="p-3 border-t border-neutral-800 bg-neutral-900/30 flex items-center justify-between">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1.5 rounded hover:bg-neutral-800 disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-neutral-400">Page {currentPage} of {totalPages}</span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-1.5 rounded hover:bg-neutral-800 disabled:opacity-30"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </aside>

        {/* Right Content - Details */}
        <main className="flex-1 overflow-y-auto bg-neutral-950/50 relative">
          {selectedPR ? (
            <div className="max-w-4xl mx-auto p-8 space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">

              {/* PR Header */}
              <div className="space-y-4 border-b border-neutral-800 pb-8">
                <div className="flex items-center gap-4">
                  <a
                    href={selectedPR.html_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-3xl font-bold text-white hover:text-blue-400 transition-colors leading-tight"
                  >
                    {selectedPR.title}
                  </a>
                  <a href={selectedPR.html_url} target="_blank" rel="noreferrer" className="shrink-0 p-2 rounded-full hover:bg-neutral-800 transition-colors text-neutral-400 hover:text-white">
                    <ExternalLink className="w-5 h-5" />
                  </a>
                </div>

                <div className="flex items-center gap-6 text-sm text-neutral-400">
                  <div className="flex items-center gap-2">
                    <img src={selectedPR.author_avatar} className="w-6 h-6 rounded-full" />
                    <span className="font-medium text-neutral-200">@{selectedPR.author}</span>
                  </div>
                  <span className={cn("px-2 py-0.5 rounded-full text-xs font-bold border", getStatusColor(selectedPR.is_draft))}>
                    {selectedPR.is_draft ? 'Draft' : 'Open'}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4" />
                    Created {new Date(selectedPR.created_at).toLocaleDateString()}
                  </span>
                </div>

                {selectedPR.labels.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedPR.labels.map(label => (
                      <span key={label} className="px-2.5 py-1 rounded-md bg-neutral-800/50 text-neutral-300 text-xs border border-neutral-700">
                        {label}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* AI Summary Section */}
              <div className="bg-gradient-to-br from-blue-900/10 to-purple-900/10 border border-blue-500/20 rounded-xl p-6 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-50">
                  <Bot className="w-24 h-24 text-blue-500/10 rotate-12" />
                </div>

                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2">
                      <Bot className="w-5 h-5" /> AI Summary
                    </h3>
                    <button
                      onClick={() => fetchSummary(selectedPR.number)}
                      disabled={loadingSummary === selectedPR.number}
                      className="px-3 py-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-xs font-medium border border-blue-500/30 transition-all flex items-center gap-2"
                    >
                      {loadingSummary === selectedPR.number ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Regenerate'}
                    </button>
                  </div>

                  {summaries[selectedPR.number] ? (
                    <div className="prose prose-invert prose-sm max-w-none text-neutral-300">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {summaries[selectedPR.number]}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <p className="text-neutral-500 text-sm mb-4">Generate an AI summary to get a quick overview of this PR.</p>
                      <button
                        onClick={() => fetchSummary(selectedPR.number)}
                        disabled={loadingSummary === selectedPR.number}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-blue-500/20"
                      >
                        {loadingSummary === selectedPR.number ? (
                          <span className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</span>
                        ) : (
                          'Summarize PR'
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Original Body */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Layout className="w-5 h-5 text-neutral-500" /> Description
                </h3>
                <div className="p-6 bg-neutral-900/30 border border-neutral-800 rounded-xl text-neutral-300 text-sm leading-relaxed whitespace-pre-wrap font-mono">
                  {selectedPR.body || <span className="text-neutral-600 italic">No description provided.</span>}
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-neutral-600 p-12">
              <div className="w-24 h-24 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-6">
                <GitPullRequest className="w-10 h-10 opacity-50" />
              </div>
              <h2 className="text-xl font-medium text-neutral-400 mb-2">No Pull Request Selected</h2>
              <p className="max-w-sm text-center">Select a pull request from the sidebar to view its details, AI summary, and more.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
