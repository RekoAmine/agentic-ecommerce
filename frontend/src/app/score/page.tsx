import { Card, CardTitle } from "@/components/ui/card";
import { scoreSegment } from "@/features/score/score";
import { dashboardMcpClient } from "@/lib/mcp/client";

export default async function ScorePage() {
  const products = await dashboardMcpClient.listProducts();
  return <section className="space-y-6"><h2 className="text-3xl font-bold">Score</h2><div className="grid gap-4">{products.map((product) => <Card key={product.id}><CardTitle>{product.title}</CardTitle><p className="mt-2 text-muted-foreground">Segment: {scoreSegment(product)}</p><div className="mt-4 h-3 rounded-full bg-muted"><div className="h-3 rounded-full bg-primary" style={{ width: `${product.score}%` }} /></div></Card>)}</div></section>;
}
