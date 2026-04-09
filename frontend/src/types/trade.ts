export interface Trade {
  _id: string;
  portfolio_id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  traded_at: string;
}

export interface TradeRequest {
  symbol: string;
  quantity: number;
  price: number;
}
