import { useEffect, useRef, useState } from 'react';
import { searchStocks } from '../services/api';

interface StockResult {
  symbol: string;
  name: string;
  exchange: string;
}

interface Props {
  onSelect: (symbol: string) => void;
  placeholder?: string;
}

export default function StockSearch({ onSelect, placeholder = 'Search stock…' }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockResult[]>([]);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchStocks(query.trim());
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 400);
  }, [query]);

  function pick(symbol: string) {
    onSelect(symbol);
    setQuery(symbol);
    setResults([]);
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {loading && (
        <p className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg p-2 text-xs text-gray-500 z-10">
          Searching…
        </p>
      )}
      {results.length > 0 && (
        <ul className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
          {results.map(r => (
            <li key={r.symbol}>
              <button
                type="button"
                onClick={() => pick(r.symbol)}
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex justify-between items-center"
              >
                <span className="font-medium">{r.symbol}</span>
                <span className="text-gray-400 text-xs truncate max-w-[60%]">{r.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
