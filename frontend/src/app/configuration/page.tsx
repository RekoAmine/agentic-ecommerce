import { Card, CardTitle } from "@/components/ui/card";
import { dashboardMcpClient } from "@/lib/mcp/client";

export default async function ConfigurationPage() {
  const configuration = await dashboardMcpClient.getConfiguration();
  return <section className="space-y-6"><h2 className="text-3xl font-bold">Configuration</h2><Card><CardTitle>Paramètres MCP</CardTitle><dl className="mt-4 grid gap-3 md:grid-cols-2"><div><dt className="text-sm text-muted-foreground">Marketplace</dt><dd className="font-semibold">{configuration.marketplace}</dd></div><div><dt className="text-sm text-muted-foreground">Devise</dt><dd className="font-semibold">{configuration.currency}</dd></div><div><dt className="text-sm text-muted-foreground">Score minimum</dt><dd className="font-semibold">{configuration.minScore}</dd></div><div><dt className="text-sm text-muted-foreground">Budget max</dt><dd className="font-semibold">${configuration.maxBudget}</dd></div></dl></Card></section>;
}
