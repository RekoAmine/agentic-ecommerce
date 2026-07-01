import type { DashboardConfiguration, DashboardEvent, DashboardOverview, DashboardProduct } from "@/types/dashboard";

/** Contract implemented by any adapter allowed to feed the dashboard. */
export interface DashboardMcpClient {
  getOverview(): Promise<DashboardOverview>;
  listProducts(): Promise<DashboardProduct[]>;
  getProduct(id: string): Promise<DashboardProduct | undefined>;
  listEvents(): Promise<DashboardEvent[]>;
  getConfiguration(): Promise<DashboardConfiguration>;
}

const products: DashboardProduct[] = [
  { id: "prod-1", asin: "B0DASH001", title: "Organisateur de cuisine pliable", category: "Home & Kitchen", price: 29.9, margin: 0.34, score: 86, status: "validated" },
  { id: "prod-2", asin: "B0DASH002", title: "Kit accessoires café premium", category: "Kitchen", price: 24.5, margin: 0.28, score: 74, status: "watch" },
  { id: "prod-3", asin: "B0DASH003", title: "Lampe LED bureau compacte", category: "Office", price: 19.99, margin: 0.18, score: 51, status: "rejected" }
];

const events: DashboardEvent[] = [
  { id: "evt-1", productId: "prod-1", label: "Score recalculé par le serveur MCP", createdAt: "2026-07-01T08:30:00Z", actor: "mcp" },
  { id: "evt-2", productId: "prod-2", label: "Analyse concurrence demandée", createdAt: "2026-06-30T14:10:00Z", actor: "agent" },
  { id: "evt-3", productId: "prod-3", label: "Produit rejeté sous le seuil de marge", createdAt: "2026-06-29T18:45:00Z", actor: "user" }
];

/** Simulated MCP client; replaceable by a transport adapter without changing UI features. */
export class SimulatedDashboardMcpClient implements DashboardMcpClient {
  async getOverview(): Promise<DashboardOverview> {
    const averageScore = Math.round(products.reduce((sum, product) => sum + product.score, 0) / products.length);
    return {
      totalProducts: products.length,
      averageScore,
      validatedProducts: products.filter((product) => product.status === "validated").length,
      monthlyRevenuePotential: 12840
    };
  }

  async listProducts() {
    return products;
  }

  async getProduct(id: string) {
    return products.find((product) => product.id === id);
  }

  async listEvents() {
    return events;
  }

  async getConfiguration() {
    return { marketplace: "Amazon US", currency: "USD", minScore: 70, maxBudget: 2500 };
  }
}

export const dashboardMcpClient: DashboardMcpClient = new SimulatedDashboardMcpClient();
