import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import RefreshButton from "@/components/RefreshButton";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GetFinance",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-gray-950 text-gray-100 min-h-screen`}>
        <nav className="border-b border-gray-800 px-6 py-3 flex gap-6 items-center">
          <span className="font-semibold text-white">GetFinance</span>
          <Link href="/transactions" className="text-gray-400 hover:text-white transition-colors">
            Transações
          </Link>
          <Link href="/query" className="text-gray-400 hover:text-white transition-colors">
            Query SQL
          </Link>
          <RefreshButton />
        </nav>
        <main className="px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
