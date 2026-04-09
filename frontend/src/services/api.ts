import type { Alert, AlertCreate } from '../types/alert';
import type { JournalCreate, JournalEntry } from '../types/journal';
import type { Portfolio, PortfolioCreate, PortfolioDetail } from '../types/portfolio';
import type { Trade, TradeRequest } from '../types/trade';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// --- Portfolios ---
export const listPortfolios = () => request<Portfolio[]>('/portfolios');
export const createPortfolio = (data: PortfolioCreate) =>
  request<Portfolio>('/portfolios', { method: 'POST', body: JSON.stringify(data) });
export const getPortfolio = (id: string) => request<PortfolioDetail>(`/portfolios/${id}`);
export const deletePortfolio = (id: string) =>
  request<void>(`/portfolios/${id}`, { method: 'DELETE' });

// --- Trades ---
export const buyStock = (portfolioId: string, data: TradeRequest) =>
  request<Trade>(`/portfolios/${portfolioId}/buy`, { method: 'POST', body: JSON.stringify(data) });
export const sellStock = (portfolioId: string, data: TradeRequest) =>
  request<Trade>(`/portfolios/${portfolioId}/sell`, { method: 'POST', body: JSON.stringify(data) });
export const getTrades = (portfolioId: string) =>
  request<Trade[]>(`/portfolios/${portfolioId}/trades`);

// --- Stocks ---
export const searchStocks = (q: string) =>
  request<{ symbol: string; name: string; exchange: string }[]>(`/stocks/search?q=${encodeURIComponent(q)}`);
export const getStockPrice = (symbol: string) =>
  request<{ symbol: string; last_price: number; fetched_at: string }>(`/stocks/${symbol}/price`);

// --- Alerts ---
export const listAlerts = () => request<Alert[]>('/alerts');
export const createAlert = (data: AlertCreate) =>
  request<Alert>('/alerts', { method: 'POST', body: JSON.stringify(data) });
export const deleteAlert = (id: string) =>
  request<void>(`/alerts/${id}`, { method: 'DELETE' });

// --- Journal ---
export const listEntries = () => request<JournalEntry[]>('/journal');
export const createEntry = (data: JournalCreate) =>
  request<JournalEntry>('/journal', { method: 'POST', body: JSON.stringify(data) });
export const deleteEntry = (id: string) =>
  request<void>(`/journal/${id}`, { method: 'DELETE' });
