"use client";

import { exportUrl } from "@/lib/api";
import type { TransactionFilters } from "@/lib/types";

type Props = {
  filters: TransactionFilters;
  resource: "transactions" | "accounts";
};

export default function ExportButton({ filters, resource }: Props) {
  const formats = ["csv", "json", "excel"] as const;

  return (
    <div className="flex gap-2 items-center">
      <span className="text-sm text-gray-400">Exportar:</span>
      {formats.map((fmt) => (
        <a
          key={fmt}
          href={exportUrl(resource, filters, fmt)}
          download
          className="text-xs px-3 py-1.5 rounded bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 hover:text-white transition-colors uppercase"
        >
          {fmt}
        </a>
      ))}
    </div>
  );
}
