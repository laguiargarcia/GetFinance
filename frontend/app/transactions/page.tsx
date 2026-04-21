"use client";

import { useEffect, useState } from "react";
import FilterBar from "@/components/FilterBar";
import TransactionTable from "@/components/TransactionTable";
import ExportButton from "@/components/ExportButton";
import { fetchTransactions, fetchCategories } from "@/lib/api";
import type { Transaction, TransactionFilters } from "@/lib/types";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCategories()
      .then((data) => setCategories(data.map((c) => c.category)))
      .catch(() => {});
  }, []);

  async function handleFilter(newFilters: TransactionFilters) {
    setFilters(newFilters);
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTransactions(newFilters);
      setTransactions(data);
    } catch (e) {
      setError("Erro ao buscar transações. API está rodando?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <FilterBar categories={categories} onFilter={handleFilter} />
        <ExportButton filters={filters} resource="transactions" />
      </div>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      {loading ? (
        <p className="text-gray-400 text-sm mt-4">Carregando...</p>
      ) : (
        <TransactionTable transactions={transactions} />
      )}
    </div>
  );
}
