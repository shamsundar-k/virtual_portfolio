import { useEffect, useRef, useState } from 'react';
import { createEntry, deleteEntry, listEntries } from '../services/api';
import type { JournalEntry } from '../types/journal';

export default function Journal() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  async function load() {
    try {
      setEntries(await listEntries());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!note.trim()) return;
    setSaving(true);
    try {
      await createEntry({ note: note.trim() });
      setNote('');
      textareaRef.current?.focus();
      load();
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteEntry(id);
      load();
    } catch {
      alert('Failed to delete note.');
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-lg mx-auto px-4 pt-6">
        <h1 className="text-xl font-bold text-gray-900 mb-4">Journal</h1>

        {/* Add note form */}
        <form onSubmit={handleAdd} className="bg-white rounded-xl shadow-sm p-4 mb-4">
          <textarea
            ref={textareaRef}
            value={note}
            onChange={e => setNote(e.target.value)}
            rows={3}
            placeholder="Write a note…"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={saving || !note.trim()}
            className="mt-2 w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Add Note'}
          </button>
        </form>

        {/* Notes list */}
        {loading ? (
          <p className="text-center text-gray-400">Loading…</p>
        ) : entries.length === 0 ? (
          <p className="text-center text-gray-400 mt-6">No notes yet. Start writing above.</p>
        ) : (
          <div className="space-y-3">
            {entries.map(e => (
              <div key={e._id} className="bg-white rounded-xl shadow-sm p-4">
                <p className="text-sm text-gray-800 whitespace-pre-wrap">{e.note}</p>
                <div className="flex justify-between items-center mt-2">
                  <p className="text-xs text-gray-400">
                    {new Date(e.created_at).toLocaleString('en-IN', {
                      day: 'numeric', month: 'short', year: 'numeric',
                      hour: '2-digit', minute: '2-digit',
                    })}
                  </p>
                  <button
                    onClick={() => handleDelete(e._id)}
                    className="text-xs text-red-400 hover:text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
