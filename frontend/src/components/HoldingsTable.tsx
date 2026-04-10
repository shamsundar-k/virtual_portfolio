import type { Holding } from '../types/portfolio';

interface Props {
  holdings: Holding[];
}

function fmt(n: number | null, prefix = '₹') {
  if (n === null) return '—';
  return `${prefix}${n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function pnlColor(n: number | null) {
  if (n === null) return 'text-gray-500';
  return n >= 0 ? 'text-green-600' : 'text-red-500';
}

export default function HoldingsTable({ holdings }: Props) {
  if (holdings.length === 0) {
    return <p className="text-gray-400 text-sm text-center py-6">No holdings yet. Buy your first stock below.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-gray-500 text-left">
            <th className="pb-2 font-medium">Symbol</th>
            <th className="pb-2 font-medium text-right">Qty</th>
            <th className="pb-2 font-medium text-right">Avg Buy</th>
            <th className="pb-2 font-medium text-right">LTP</th>
            <th className="pb-2 font-medium text-right">Unrealised P&L</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map(h => (
            <tr key={h.symbol} className="border-b border-gray-100 last:border-0">
              <td className="py-2 font-semibold">{h.symbol}</td>
              <td className="py-2 text-right">{h.quantity}</td>
              <td className="py-2 text-right">{fmt(h.avg_buy_price)}</td>
              <td className="py-2 text-right">{fmt(h.current_price)}</td>
              <td className={`py-2 text-right font-medium ${pnlColor(h.unrealized_pnl)}`}>
                {fmt(h.unrealized_pnl)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
