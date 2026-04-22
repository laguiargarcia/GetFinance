"use client";

import { useState } from "react";
import ResultTable from "@/components/ResultTable";
import { runQuery } from "@/lib/api";
import type { QueryResult } from "@/lib/types";

function escapeCsv(value: unknown): string {
  const str = String(value ?? "");
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

const DEFAULT_SQL = `SELECT date, description, amount, category
FROM delta_scan('etl/data/cleansed/transactions')
ORDER BY date DESC
LIMIT 20`;

export default function QueryPage() {
  const [sql, setSql] = useState(DEFAULT_SQL);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleRun() {
    setLoading(true);
    try {
      const data = await runQuery(sql);
      setResult(data);
    } catch (e) {
      setResult({ columns: [], rows: [], error: "Erro ao conectar na API." });
    } finally {
      setLoading(false);
    }
  }

  function exportCsv() {
    if (!result || result.error || result.rows.length === 0) return;
    const lines = [result.columns.map(escapeCsv).join(",")];
    for (const row of result.rows) {
      lines.push(row.map(escapeCsv).join(","));
    }
    const blob = new Blob([lines.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "query_result.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="sql-editor" className="text-sm text-gray-400">SQL</label>
        <textarea
          id="sql-editor"
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          rows={8}
          className="w-full bg-gray-900 border border-gray-700 rounded px-4 py-3 text-sm font-mono text-white resize-y focus:outline-none focus:border-blue-500"
          spellCheck={false}
        />
      </div>
      <div className="flex gap-3">
        <button
          onClick={handleRun}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded text-sm transition-colors"
        >
          {loading ? "Executando..." : "Executar"}
        </button>
        {result && !result.error && result.rows.length > 0 && (
          <button
            onClick={exportCsv}
            className="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 px-4 py-2 rounded text-sm transition-colors"
          >
            Exportar CSV
          </button>
        )}
      </div>
      {result?.error && (
        <pre className="bg-red-950 border border-red-800 text-red-300 rounded px-4 py-3 text-sm overflow-x-auto">
          {result.error}
        </pre>
      )}
      {result && !result.error && (
        <ResultTable columns={result.columns} rows={result.rows} />
      )}
    </div>
  );
}
