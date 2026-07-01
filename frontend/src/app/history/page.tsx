import { Card, CardTitle } from "@/components/ui/card";
import { dashboardMcpClient } from "@/lib/mcp/client";

export default async function HistoryPage() {
  const events = await dashboardMcpClient.listEvents();
  return <section className="space-y-6"><h2 className="text-3xl font-bold">Historique</h2>{events.map((event) => <Card key={event.id}><CardTitle>{event.label}</CardTitle><p className="text-sm text-muted-foreground">{new Date(event.createdAt).toLocaleString("fr-FR")} · {event.actor}</p></Card>)}</section>;
}
