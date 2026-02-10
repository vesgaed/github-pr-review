import { useState } from 'react';
import {
  Github,
  Search,
  GitPullRequest,
  Clock,
  ExternalLink,
  Loader2,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
import { UserRepositories } from './components/UserRepositories';

// Helper for Tailwind classes
function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

interface PullRequest {
  number: number;
  title: string;
  author: string;
  html_url: string;
  labels: string[];
  is_draft: boolean;
  state: string;
  created_at: string;
  updated_at: string;
}

interface ApiResponse {
  items: PullRequest[];
  pages_fetched: number;
  from_cache: boolean;
  repository: string;
}

export default function App() {
  const [repository, setRepository] = useState('vercel/next.js');
  const [token, setToken] = useState('');
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxPages, setMaxPages] = useState(3);
  const [bypassCache, setBypassCache] = useState(false);

  const fetchData = async (repoName: string) => {
    setLoading(true);
    setError(null);
    setData(null);

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

  const getStatusColor = (isDraft: boolean) => {
    if (isDraft) return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    return 'bg-green-500/10 text-green-500 border-green-500/20';
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans selection:bg-blue-500/30">
      <header className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-neutral-800 rounded-xl">
              <Github className="w-6 h-6 text-white" />
            </div>
            <h1 className="font-bold text-lg tracking-tight">PR Status <span className="text-neutral-500 font-medium">Explorer</span></h1>
          </div>
          <div className="flex items-center gap-4 text-sm text-neutral-400">
            <a href="https://github.com/settings/tokens" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-1">
              Generate Token <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12 space-y-8">
        {/* Search / Config Panel */}
        <section className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-6 shadow-2xl backdrop-blur-sm">
          <form onSubmit={handleFetch} className="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div className="md:col-span-4 space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500">Repository</label>
              <div className="relative group">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500 group-focus-within:text-blue-400 transition-colors" />
                <input
                  type="text"
                  value={repository}
                  onChange={(e) => setRepository(e.target.value)}
                  placeholder="owner/name"
                  className="w-full bg-neutral-950/50 border border-neutral-800 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder:text-neutral-600"
                />
              </div>
            </div>

            <div className="md:col-span-4 space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500">GitHub Token (Optional)</label>
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="ghp_..."
                className="w-full bg-neutral-950/50 border border-neutral-800 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder:text-neutral-600"
              />
            </div>

            <div className="md:col-span-2 space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500">Max Pages</label>
              <input
                type="number"
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                min={1}
                max={10}
                className="w-full bg-neutral-950/50 border border-neutral-800 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
              />
            </div>

            <div className="md:col-span-2 flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_-5px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_-5px_rgba(37,99,235,0.5)]"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Fetch PRs'}
              </button>
            </div>
          </form>

          <div className="mt-4 flex items-center gap-6 text-sm text-neutral-400">
            <label className="flex items-center gap-2 cursor-pointer hover:text-white transition-colors select-none">
              <input
                type="checkbox"
                checked={bypassCache}
                onChange={(e) => setBypassCache(e.target.checked)}
                className="w-4 h-4 rounded border-neutral-700 bg-neutral-900 focus:ring-offset-0 focus:ring-blue-500 text-blue-600"
              />
              Bypass Cache
            </label>
          </div>
        </section>

        {/* User Repositories (Only if token is present) */}
        {token && (
          <UserRepositories token={token} onSelectRepo={handleSelectRepo} />
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
            <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="font-medium">{error}</p>
          </div>
        )}

        {/* Results */}
        {data && (
          <section className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h2 className="text-2xl font-bold">Open Pull Requests</h2>
                <span className="px-3 py-1 rounded-full bg-neutral-800 text-neutral-300 text-xs font-medium border border-neutral-700">
                  {data.items.length} items
                </span>
                {data.from_cache && (
                  <span className="px-2 py-0.5 rounded-md bg-yellow-500/10 text-yellow-500 text-[10px] font-bold uppercase tracking-wider border border-yellow-500/20">
                    Cached
                  </span>
                )}
              </div>
            </div>

            <div className="grid gap-3">
              {data.items.map((pr) => (
                <a
                  key={pr.number}
                  href={pr.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative bg-neutral-900 border border-neutral-800 hover:border-neutral-700 rounded-xl p-4 transition-all hover:shadow-xl hover:shadow-neutral-900/50 hover:-translate-y-0.5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider", getStatusColor(pr.is_draft))}>
                          {pr.is_draft ? 'Draft' : 'Open'}
                        </span>
                        <span className="text-neutral-500 text-xs font-mono">#{pr.number}</span>
                        <span className="text-neutral-500 text-xs">•</span>
                        <span className="text-neutral-400 text-xs flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(pr.updated_at).toLocaleDateString()}
                        </span>
                      </div>
                      <h3 className="font-semibold text-neutral-200 group-hover:text-blue-400 transition-colors truncate pr-8">
                        {pr.title}
                      </h3>
                      <div className="flex items-center gap-2 mt-2 text-xs text-neutral-500">
                        <span className="font-medium text-neutral-400">@{pr.author}</span>
                        {pr.labels.length > 0 && (
                          <div className="flex items-center gap-2 overflow-hidden">
                            {pr.labels.slice(0, 3).map(label => (
                              <span key={label} className="px-1.5 py-0.5 rounded bg-neutral-800 text-neutral-400 border border-neutral-700/50 whitespace-nowrap">
                                {label}
                              </span>
                            ))}
                            {pr.labels.length > 3 && <span>+{pr.labels.length - 3}</span>}
                          </div>
                        )}
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-neutral-700 group-hover:text-neutral-500 transition-colors self-center" />
                  </div>
                </a>
              ))}
            </div>

            {data.items.length === 0 && (
              <div className="text-center py-20 bg-neutral-900/50 border-2 border-dashed border-neutral-800 rounded-2xl">
                <GitPullRequest className="w-10 h-10 text-neutral-700 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-neutral-400">No open pull requests found</h3>
                <p className="text-neutral-500 mt-2">Try adjusting your filters or checking another repository.</p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
