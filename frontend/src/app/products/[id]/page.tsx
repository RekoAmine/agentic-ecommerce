import { notFound } from "next/navigation";
import { Card, CardTitle } from "@/components/ui/card";
import { dashboardMcpClient } from "@/lib/mcp/client";
import { scoreSegment } from "@/features/score/score";

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await dashboardMcpClient.getProduct(id);
  if (!product) notFound();
  return <section className="space-y-6"><div><h2 className="text-3xl font-bold">Produit</h2><p className="text-muted-foreground">{product.title}</p></div><div className="grid gap-4 md:grid-cols-3"><Card><CardTitle>Prix</CardTitle><p className="mt-4 text-3xl font-bold">${product.price}</p></Card><Card><CardTitle>Marge</CardTitle><p className="mt-4 text-3xl font-bold">{Math.round(product.margin * 100)}%</p></Card><Card><CardTitle>Score</CardTitle><p className="mt-4 text-3xl font-bold">{product.score} · {scoreSegment(product)}</p></Card></div></section>;
}
