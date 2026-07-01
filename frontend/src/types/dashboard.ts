/** Product summary exposed by the MCP dashboard boundary. */
export interface DashboardProduct {
  id: string;
  asin: string;
  title: string;
  category: string;
  price: number;
  margin: number;
  score: number;
  status: "watch" | "validated" | "rejected";
}

/** Historical MCP action or analysis event displayed in the dashboard. */
export interface DashboardEvent {
  id: string;
  productId: string;
  label: string;
  createdAt: string;
  actor: "mcp" | "agent" | "user";
}

/** Dashboard-level settings mirrored from the MCP server. */
export interface DashboardConfiguration {
  marketplace: string;
  currency: string;
  minScore: number;
  maxBudget: number;
}

export interface DashboardOverview {
  totalProducts: number;
  averageScore: number;
  validatedProducts: number;
  monthlyRevenuePotential: number;
}
