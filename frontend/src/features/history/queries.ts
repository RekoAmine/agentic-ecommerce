import { useQuery } from "@tanstack/react-query";
import { dashboardMcpClient } from "@/lib/mcp/client";
import { dashboardQueryKeys } from "@/lib/query/keys";

/** Lists dashboard events supplied by MCP. */
export function useDashboardEvents() {
  return useQuery({ queryKey: dashboardQueryKeys.events, queryFn: () => dashboardMcpClient.listEvents() });
}
