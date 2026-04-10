import { useState } from 'react';
import { createAlert } from '../services/api';
import type { AlertCreate } from '../types/alert';
import StockSearch from './StockSearch';

interface Props {
  onDone: () => void;
}

export default function AlertForm({ onDone }: Props) {
  const [symbol, setSymbol] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [condition, setCondition] = useState<'ABOVE' | 'BELOW'>('ABOVE');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!symbol || !targetPrice) {
      setError('Symbol and target price are required.');
      return;
    }
    setLoading(true);
    try {
      const payload: AlertCreate = { symbol, target_price: Number(targetPrice), condition };
      await createAlert(payload);
      setSymbol('');
      setTargetPrice('');
      setCondition('ABOVE');
      onDone();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create alert.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <StockSearch onSelect={setSymbol} placeholder="Search & select stock" />
      <input
        type="number"
        min="0"
        step="0.01"
        value={targetPrice}
        onChange={e => setTargetPrice(e.target.value)}
        placeholder="Target price (₹)"
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <div className="flex gap-2">
        {(['ABOVE', 'BELOW'] as const).map(c => (
          <button
            key={c}
            type="button"
            onClick={() => setCondition(c)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
              condition === c ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {c}
          </button>
        ))}
      </div>
      {error && <p className="text-red-500 text-xs">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50"
      >
        {loading ? 'Creating…' : 'Create Alert'}
      </button>
    </form>
  );
}
