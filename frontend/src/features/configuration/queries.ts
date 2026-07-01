import { useQuery } from "@tanstack/react-query";
import { dashboardMcpClient } from "@/lib/mcp/client";
import { dashboardQueryKeys } from "@/lib/query/keys";

/** Loads dashboard configuration from the MCP boundary. */
export function useDashboardConfiguration() {
  return useQuery({ queryKey: dashboardQueryKeys.configuration, queryFn: () => dashboardMcpClient.getConfiguration() });
}
