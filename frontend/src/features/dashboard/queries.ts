import { useQuery } from "@tanstack/react-query";
import { dashboardMcpClient } from "@/lib/mcp/client";
import { dashboardQueryKeys } from "@/lib/query/keys";

/** Read-only overview query routed through the dashboard MCP client. */
export function useDashboardOverview() {
  return useQuery({ queryKey: dashboardQueryKeys.overview, queryFn: () => dashboardMcpClient.getOverview() });
}
