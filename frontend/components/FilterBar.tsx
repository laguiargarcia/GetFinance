"use client";

import { useState } from "react";
import type { TransactionFilters } from "@/lib/types";

type Props = {
  categories: string[];
  onFilter: (filters: TransactionFilters) => void;
};

export default function FilterBar({ categories, onFilter }: Props) {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [category, setCategory] = useState("");
  const [type, setType] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onFilter({
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      category: category || undefined,
      type: type || undefined,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400">De</label>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-white"
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400">Até</label>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-white"
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400">Categoria</label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-white"
        >
          <option value="">Todas</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400">Tipo</label>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-white"
        >
          <option value="">Todos</option>
          <option value="CREDIT">Crédito</option>
          <option value="DEBIT">Débito</option>
        </select>
      </div>
      <button
        type="submit"
        className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded text-sm transition-colors"
      >
        Filtrar
      </button>
    </form>
  );
}
