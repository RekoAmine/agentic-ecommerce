import { useQuery } from "@tanstack/react-query";
import { dashboardMcpClient } from "@/lib/mcp/client";
import { dashboardQueryKeys } from "@/lib/query/keys";

/** Lists products via MCP without importing connector adapters. */
export function useProducts() {
  return useQuery({ queryKey: dashboardQueryKeys.products, queryFn: () => dashboardMcpClient.listProducts() });
}

/** Loads one product via MCP by its dashboard identifier. */
export function useProduct(id: string) {
  return useQuery({ queryKey: dashboardQueryKeys.product(id), queryFn: () => dashboardMcpClient.getProduct(id) });
}
