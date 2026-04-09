import { useEffect, useState } from 'react';
import AlertForm from '../components/AlertForm';
import { deleteAlert, listAlerts } from '../services/api';
import type { Alert } from '../types/alert';

function fmt(n: number) {
  return `₹${n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  async function load() {
    try {
      setAlerts(await listAlerts());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleDelete(id: string) {
    try {
      await deleteAlert(id);
      load();
    } catch {
      alert('Failed to delete alert.');
    }
  }

  const active = alerts.filter(a => a.is_active);
  const triggered = alerts.filter(a => !a.is_active);

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-lg mx-auto px-4 pt-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-900">Price Alerts</h1>
          <button
            onClick={() => setShowForm(v => !v)}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg font-medium"
          >
            {showForm ? 'Cancel' : '+ New'}
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-xl shadow-sm p-4 mb-4">
            <AlertForm onDone={() => { setShowForm(false); load(); }} />
          </div>
        )}

        {loading ? (
          <p className="text-center text-gray-400 mt-10">Loading…</p>
        ) : (
          <>
            {active.length > 0 && (
              <div className="mb-4">
                <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Active</h2>
                <div className="space-y-2">
                  {active.map(a => (
                    <div key={a._id} className="bg-white rounded-xl shadow-sm p-3 flex justify-between items-center">
                      <div>
                        <p className="font-semibold text-gray-900">{a.symbol}</p>
                        <p className="text-xs text-gray-500">
                          {a.condition} {fmt(a.target_price)}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDelete(a._id)}
                        className="text-xs text-red-400 hover:text-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {triggered.length > 0 && (
              <div>
                <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Triggered</h2>
                <div className="space-y-2">
                  {triggered.map(a => (
                    <div key={a._id} className="bg-gray-100 rounded-xl p-3 flex justify-between items-center opacity-70">
                      <div>
                        <p className="font-semibold text-gray-700">{a.symbol}</p>
                        <p className="text-xs text-gray-500">
                          {a.condition} {fmt(a.target_price)}
                          {a.triggered_at && ` · ${new Date(a.triggered_at).toLocaleDateString('en-IN')}`}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDelete(a._id)}
                        className="text-xs text-red-400 hover:text-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {alerts.length === 0 && (
              <p className="text-center text-gray-400 mt-10">No alerts yet. Create one to get notified on Telegram.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
