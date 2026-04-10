export interface Portfolio {
  _id: string;
  name: string;
  starting_amount: number;
  current_cash: number;
  created_at: string;
}

export interface PortfolioCreate {
  name: string;
  starting_amount: number;
}

export interface Holding {
  symbol: string;
  quantity: number;
  avg_buy_price: number;
  current_price: number | null;
  unrealized_pnl: number | null;
}

export interface PortfolioDetail extends Portfolio {
  holdings: Holding[];
  total_value: number;
  total_pnl: number;
}
