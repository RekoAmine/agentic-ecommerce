import type { DashboardProduct } from "@/types/dashboard";

/** Converts a numeric product score into an explainable business segment. */
export function scoreSegment(product: Pick<DashboardProduct, "score">): "opportunité" | "surveillance" | "risque" {
  if (product.score >= 80) return "opportunité";
  if (product.score >= 60) return "surveillance";
  return "risque";
}
