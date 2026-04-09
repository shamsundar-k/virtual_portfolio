import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import HoldingsTable from '../components/HoldingsTable';
import TradeForm from '../components/TradeForm';
import { getPortfolio } from '../services/api';
import type { PortfolioDetail } from '../types/portfolio';

function fmt(n: number) {
  return `₹${n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function pnlColor(n: number) {
  return n >= 0 ? 'text-green-600' : 'text-red-500';
}

export default function Portfolio() {
  const { id } = useParams<{ id: string }>();
  const [portfolio, setPortfolio] = useState<PortfolioDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showTrade, setShowTrade] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    if (!id) return;
    setError('');
    try {
      setPortfolio(await getPortfolio(id));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load portfolio.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [id]);

  function handleTradeDone() {
    setShowTrade(false);
    load();
  }

  if (loading) return <p className="text-center text-gray-400 mt-20">Loading…</p>;
  if (error) return <p className="text-center text-red-400 mt-20">{error}</p>;
  if (!portfolio) return null;

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-lg mx-auto px-4 pt-6">
        <h1 className="text-xl font-bold text-gray-900 mb-1">{portfolio.name}</h1>

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div className="bg-white rounded-xl p-3 shadow-sm text-center">
            <p className="text-xs text-gray-400">Cash</p>
            <p className="text-sm font-semibold text-gray-800 mt-0.5">{fmt(portfolio.current_cash)}</p>
          </div>
          <div className="bg-white rounded-xl p-3 shadow-sm text-center">
            <p className="text-xs text-gray-400">Total Value</p>
            <p className="text-sm font-semibold text-gray-800 mt-0.5">{fmt(portfolio.total_value)}</p>
          </div>
          <div className="bg-white rounded-xl p-3 shadow-sm text-center">
            <p className="text-xs text-gray-400">P&L</p>
            <p className={`text-sm font-semibold mt-0.5 ${pnlColor(portfolio.total_pnl)}`}>
              {fmt(portfolio.total_pnl)}
            </p>
          </div>
        </div>

        {/* Holdings */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-4">
          <h2 className="font-semibold text-gray-800 mb-3">Holdings</h2>
          <HoldingsTable holdings={portfolio.holdings} />
        </div>

        {/* Trade form toggle */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-gray-800">Trade</h2>
            <button
              onClick={() => setShowTrade(v => !v)}
              className="text-sm text-blue-600 font-medium"
            >
              {showTrade ? 'Cancel' : 'Open'}
            </button>
          </div>
          {showTrade && id && (
            <TradeForm portfolioId={id} onDone={handleTradeDone} />
          )}
        </div>
      </div>
    </div>
  );
}
