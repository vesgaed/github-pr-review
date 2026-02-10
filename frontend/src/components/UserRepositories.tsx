import { useState, useEffect } from 'react';
import { Book, Lock, Globe, Loader2, RefreshCw } from 'lucide-react';

interface Repository {
    full_name: string;
    private: boolean;
    html_url: string;
    description: string;
    updated_at: string;
}

interface UserRepositoriesProps {
    token: string;
    onSelectRepo: (repoName: string) => void;
}

export function UserRepositories({ token, onSelectRepo }: UserRepositoriesProps) {
    const [repos, setRepos] = useState<Repository[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchRepos = async () => {
        if (!token) return;
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/user/repos?token=${token}`);
            if (!response.ok) {
                throw new Error('Failed to fetch repositories. Check your token.');
            }
            const data = await response.json();
            setRepos(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) {
            fetchRepos();
        } else {
            setRepos([]);
        }
    }, [token]);

    if (!token) return null;

    return (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-6 shadow-2xl backdrop-blur-sm animate-in fade-in slide-in-from-bottom-2">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-neutral-500 flex items-center gap-2">
                    <Book className="w-4 h-4" />
                    My Repositories
                </h3>
                <button
                    onClick={fetchRepos}
                    disabled={loading}
                    className="p-1.5 hover:bg-neutral-800 rounded-lg text-neutral-500 hover:text-white transition-colors"
                    title="Refresh Repositories"
                >
                    <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {error && (
                <p className="text-red-400 text-sm mb-4">{error}</p>
            )}

            {loading && repos.length === 0 ? (
                <div className="flex justify-center py-4">
                    <Loader2 className="w-5 h-5 animate-spin text-neutral-600" />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-60 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-neutral-800 scrollbar-track-transparent">
                    {repos.map((repo) => (
                        <button
                            key={repo.full_name}
                            onClick={() => onSelectRepo(repo.full_name)}
                            className="text-left p-3 rounded-xl bg-neutral-950/50 border border-neutral-800 hover:border-blue-500/50 hover:bg-neutral-800 transition-all group"
                        >
                            <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-sm text-neutral-200 group-hover:text-blue-400 truncate w-full">
                                    {repo.full_name}
                                </span>
                                {repo.private ? (
                                    <Lock className="w-3 h-3 text-yellow-500/70" />
                                ) : (
                                    <Globe className="w-3 h-3 text-neutral-600" />
                                )}
                            </div>
                            <p className="text-[10px] text-neutral-500 truncate">
                                {new Date(repo.updated_at).toLocaleDateString()}
                            </p>
                        </button>
                    ))}
                    {repos.length === 0 && !loading && (
                        <p className="text-neutral-500 text-sm italic col-span-full text-center py-2">No repositories found.</p>
                    )}
                </div>
            )}
        </div>
    );
}
