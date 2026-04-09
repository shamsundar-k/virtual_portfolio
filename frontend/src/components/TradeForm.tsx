import { useState } from 'react';
import { buyStock, getStockPrice, sellStock } from '../services/api';
import StockSearch from './StockSearch';

interface Props {
  portfolioId: string;
  onDone: () => void;
}

export default function TradeForm({ portfolioId, onDone }: Props) {
  const [symbol, setSymbol] = useState('');
  const [tradeType, setTradeType] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function fetchLTP(sym: string) {
    setSymbol(sym);
    try {
      const data = await getStockPrice(sym);
      setPrice(String(data.last_price));
    } catch {
      setPrice('');
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!symbol || !quantity || !price) {
      setError('All fields are required.');
      return;
    }
    setLoading(true);
    try {
      const payload = { symbol, quantity: Number(quantity), price: Number(price) };
      if (tradeType === 'BUY') {
        await buyStock(portfolioId, payload);
      } else {
        await sellStock(portfolioId, payload);
      }
      setSymbol('');
      setQuantity('');
      setPrice('');
      onDone();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Trade failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        {(['BUY', 'SELL'] as const).map(t => (
          <button
            key={t}
            type="button"
            onClick={() => setTradeType(t)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
              tradeType === t
                ? t === 'BUY'
                  ? 'bg-green-600 text-white'
                  : 'bg-red-500 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      <StockSearch onSelect={fetchLTP} placeholder="Search & select stock" />
      <input
        type="number"
        min="1"
        value={quantity}
        onChange={e => setQuantity(e.target.value)}
        placeholder="Quantity"
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        type="number"
        min="0"
        step="0.01"
        value={price}
        onChange={e => setPrice(e.target.value)}
        placeholder="Price (₹)"
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {error && <p className="text-red-500 text-xs">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50"
      >
        {loading ? 'Processing…' : `${tradeType} ${symbol || 'Stock'}`}
      </button>
    </form>
  );
}
