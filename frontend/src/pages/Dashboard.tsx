import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPortfolio, deletePortfolio, listPortfolios } from '../services/api';
import type { Portfolio, PortfolioCreate } from '../types/portfolio';

function fmt(n: number) {
  return `₹${n.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);

  async function load() {
    try {
      setPortfolios(await listPortfolios());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!name.trim() || !amount) {
      setError('Name and starting amount are required.');
      return;
    }
    setCreating(true);
    try {
      const data: PortfolioCreate = { name: name.trim(), starting_amount: Number(amount) };
      await createPortfolio(data);
      setName('');
      setAmount('');
      setShowForm(false);
      load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create portfolio.');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this portfolio and all its trades?')) return;
    try {
      await deletePortfolio(id);
      load();
    } catch {
      alert('Failed to delete portfolio.');
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-lg mx-auto px-4 pt-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-900">Portfolios</h1>
          {portfolios.length < 10 && (
            <button
              onClick={() => setShowForm(v => !v)}
              className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg font-medium"
            >
              {showForm ? 'Cancel' : '+ New'}
            </button>
          )}
        </div>

        {showForm && (
          <form onSubmit={handleCreate} className="bg-white rounded-xl shadow-sm p-4 mb-4 space-y-3">
            <h2 className="font-semibold text-gray-800">New Portfolio</h2>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Portfolio name"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              min="1"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              placeholder="Starting amount (₹)"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {error && <p className="text-red-500 text-xs">{error}</p>}
            <button
              type="submit"
              disabled={creating}
              className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50"
            >
              {creating ? 'Creating…' : 'Create Portfolio'}
            </button>
          </form>
        )}

        {loading ? (
          <p className="text-center text-gray-400 mt-10">Loading…</p>
        ) : portfolios.length === 0 ? (
          <p className="text-center text-gray-400 mt-10">No portfolios yet. Create one to get started.</p>
        ) : (
          <div className="space-y-3">
            {portfolios.map(p => (
              <div
                key={p._id}
                className="bg-white rounded-xl shadow-sm p-4 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate(`/portfolio/${p._id}`)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="font-semibold text-gray-900">{p.name}</h2>
                    <p className="text-xs text-gray-400 mt-0.5">
                      Started with {fmt(p.starting_amount)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-700">{fmt(p.current_cash)} cash</p>
                    <button
                      onClick={e => { e.stopPropagation(); handleDelete(p._id); }}
                      className="text-xs text-red-400 hover:text-red-600 mt-1"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
