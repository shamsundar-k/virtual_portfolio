export interface JournalEntry {
  _id: string;
  note: string;
  created_at: string;
}

export interface JournalCreate {
  note: string;
}
