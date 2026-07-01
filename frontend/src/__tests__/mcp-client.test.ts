import { describe, expect, it } from "vitest";
import { SimulatedDashboardMcpClient } from "@/lib/mcp/client";

describe("SimulatedDashboardMcpClient", () => {
  it("exposes dashboard data through the MCP boundary", async () => {
    const client = new SimulatedDashboardMcpClient();
    await expect(client.listProducts()).resolves.toHaveLength(3);
    await expect(client.getConfiguration()).resolves.toMatchObject({ marketplace: "Amazon US" });
  });

  it("computes a stable overview from MCP products", async () => {
    const client = new SimulatedDashboardMcpClient();
    await expect(client.getOverview()).resolves.toMatchObject({ totalProducts: 3, averageScore: 70, validatedProducts: 1 });
  });
});
