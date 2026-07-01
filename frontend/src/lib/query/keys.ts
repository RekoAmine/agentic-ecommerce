/** Stable TanStack Query keys for all dashboard data requested through MCP. */
export const dashboardQueryKeys = {
  overview: ["mcp", "dashboard", "overview"] as const,
  products: ["mcp", "dashboard", "products"] as const,
  product: (id: string) => ["mcp", "dashboard", "products", id] as const,
  events: ["mcp", "dashboard", "events"] as const,
  configuration: ["mcp", "dashboard", "configuration"] as const
};
