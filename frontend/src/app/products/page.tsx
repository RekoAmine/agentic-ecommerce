import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardTitle } from "@/components/ui/card";
import { dashboardMcpClient } from "@/lib/mcp/client";

export default async function ProductsPage() {
  const products = await dashboardMcpClient.listProducts();
  return <section className="space-y-6"><h2 className="text-3xl font-bold">Produits</h2><div className="grid gap-4">{products.map((product) => <Card key={product.id} className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><div><CardTitle>{product.title}</CardTitle><p className="text-sm text-muted-foreground">{product.asin} · {product.category}</p></div><div className="flex items-center gap-4"><Badge>{product.status}</Badge><span className="font-semibold">Score {product.score}</span><Link className="text-primary underline" href={`/products/${product.id}`}>Produit</Link></div></Card>)}</div></section>;
}
