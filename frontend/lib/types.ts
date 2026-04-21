export type Transaction = {
  date: string;
  description: string;
  amount: number;
  category: string;
  type: "CREDIT" | "DEBIT";
  currency_code: string;
  account_id: string;
  status: string;
  operation_type: string;
};

export type Account = {
  id: string;
  name: string;
  number: string;
  balance: number;
  currency_code: string;
  type: string;
  subtype: string;
};

export type TransactionFilters = {
  date_from?: string;
  date_to?: string;
  category?: string;
  type?: string;
  format?: string;
};

export type QueryResult = {
  columns: string[];
  rows: unknown[][];
  error?: string;
};
