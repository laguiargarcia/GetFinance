const BASE = "http://localhost:8000";

export async function fetchTransactions(filters: import("./types").TransactionFilters): Promise<import("./types").Transaction[]> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.category) params.set("category", filters.category);
  if (filters.type) params.set("type", filters.type);
  params.set("format", "json");

  const res = await fetch(`${BASE}/transactions?${params}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function fetchCategories(): Promise<{ category: string; count: number }[]> {
  const res = await fetch(`${BASE}/categories`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export function exportUrl(path: "transactions" | "accounts", filters: import("./types").TransactionFilters, format: string): string {
  const params = new URLSearchParams({ format });
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.category) params.set("category", filters.category);
  if (filters.type) params.set("type", filters.type);
  return `${BASE}/${path}?${params}`;
}

export async function runQuery(sql: string): Promise<import("./types").QueryResult> {
  const res = await fetch(`${BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sql }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
