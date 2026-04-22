"use client";

import { useState } from "react";

export default function RefreshButton() {
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");

  async function handleRefresh() {
    setStatus("loading");
    try {
      const res = await fetch("http://localhost:8000/refresh", { method: "POST" });
      setStatus(res.ok ? "ok" : "error");
    } catch {
      setStatus("error");
    } finally {
      setTimeout(() => setStatus("idle"), 3000);
    }
  }

  const label =
    status === "loading" ? "Atualizando..." :
    status === "ok" ? "Atualizado ✓" :
    status === "error" ? "Erro ✗" :
    "Atualizar dados";

  return (
    <button
      onClick={handleRefresh}
      disabled={status === "loading"}
      className={`ml-auto text-xs px-3 py-1.5 rounded border transition-colors disabled:opacity-50 ${
        status === "ok" ? "border-green-700 text-green-400" :
        status === "error" ? "border-red-700 text-red-400" :
        "border-gray-700 text-gray-400 hover:text-white hover:border-gray-500"
      }`}
    >
      {label}
    </button>
  );
}
