import { Card, CardTitle } from "@/components/ui/card";
import { dashboardMcpClient } from "@/lib/mcp/client";

export default async function DashboardPage() {
  const overview = await dashboardMcpClient.getOverview();
  return <section className="space-y-6"><div><h2 className="text-3xl font-bold">Dashboard</h2><p className="text-muted-foreground">Vue exécutive des opportunités FBA consolidées par le serveur MCP.</p></div><div className="grid gap-4 md:grid-cols-4">{[["Produits", overview.totalProducts], ["Score moyen", overview.averageScore], ["Validés", overview.validatedProducts], ["Potentiel mensuel", `$${overview.monthlyRevenuePotential.toLocaleString()}`]].map(([label, value]) => <Card key={label.toString()}><CardTitle>{label}</CardTitle><p className="mt-4 text-3xl font-bold">{value}</p></Card>)}</div></section>;
}
