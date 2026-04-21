"use client";

import { useState } from "react";
import type { Transaction } from "@/lib/types";

const PAGE_SIZE = 50;

type Props = { transactions: Transaction[] };

export default function TransactionTable({ transactions }: Props) {
  const [page, setPage] = useState(0);
  const total = transactions.length;
  const pageCount = Math.ceil(total / PAGE_SIZE);
  const rows = transactions.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  if (total === 0) {
    return <p className="text-gray-500 text-sm mt-4">Nenhuma transação encontrada.</p>;
  }

  return (
    <div className="mt-4">
      <div className="overflow-x-auto rounded border border-gray-800">
        <table className="w-full text-sm">
          <thead className="bg-gray-800 text-gray-400">
            <tr>
              {["Data", "Descrição", "Valor", "Categoria", "Tipo", "Status"].map((h) => (
                <th key={h} className="text-left px-3 py-2 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((tx, i) => (
              <tr key={i} className="border-t border-gray-800 hover:bg-gray-900">
                <td className="px-3 py-2 whitespace-nowrap">{tx.date}</td>
                <td className="px-3 py-2 max-w-xs truncate">{tx.description}</td>
                <td className={`px-3 py-2 font-mono whitespace-nowrap ${tx.amount < 0 ? "text-red-400" : "text-green-400"}`}>
                  {tx.amount.toLocaleString("pt-BR", { style: "currency", currency: tx.currency_code || "BRL" })}
                </td>
                <td className="px-3 py-2">{tx.category}</td>
                <td className="px-3 py-2">{tx.type}</td>
                <td className="px-3 py-2 text-gray-400">{tx.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {pageCount > 1 && (
        <div className="flex gap-2 mt-3 items-center text-sm text-gray-400">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-2 py-1 rounded bg-gray-800 disabled:opacity-40"
          >
            ←
          </button>
          <span>Página {page + 1} de {pageCount} ({total} registros)</span>
          <button
            onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
            disabled={page === pageCount - 1}
            className="px-2 py-1 rounded bg-gray-800 disabled:opacity-40"
          >
            →
          </button>
        </div>
      )}
    </div>
  );
}
