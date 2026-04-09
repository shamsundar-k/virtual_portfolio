export interface Alert {
  _id: string;
  symbol: string;
  target_price: number;
  condition: 'ABOVE' | 'BELOW';
  is_active: boolean;
  created_at: string;
  triggered_at: string | null;
}

export interface AlertCreate {
  symbol: string;
  target_price: number;
  condition: 'ABOVE' | 'BELOW';
}
