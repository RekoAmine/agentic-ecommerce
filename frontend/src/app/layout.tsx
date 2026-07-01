import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = { title: "Agentic Ecommerce Dashboard", description: "MCP-only Amazon FBA dashboard" };

const navItems = [
  ["Dashboard", "/"], ["Produits", "/products"], ["Score", "/score"], ["Historique", "/history"], ["Configuration", "/configuration"]
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="fr"><body><Providers><div className="min-h-screen"><aside className="fixed hidden h-full w-64 border-r bg-white p-6 md:block"><h1 className="text-xl font-bold">FBA Advisor</h1><p className="mt-2 text-sm text-muted-foreground">Dashboard alimenté uniquement par MCP.</p><nav className="mt-8 grid gap-2">{navItems.map(([label, href]) => <Link className="rounded-lg px-3 py-2 text-sm font-medium hover:bg-muted" href={href} key={href}>{label}</Link>)}</nav></aside><main className="p-6 md:ml-64 md:p-10">{children}</main></div></Providers></body></html>;
}
