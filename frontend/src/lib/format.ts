export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function formatRelativeDays(iso: string | null | undefined): string {
  if (!iso) return "Never";
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / (1000 * 60 * 60 * 24));
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  return `${days} days ago`;
}

export function formatQuietHours(start: number, end: number): string {
  const fmt = (h: number) => `${String(h).padStart(2, "0")}:00`;
  return `${fmt(start)} – ${fmt(end)}`;
}

export function hobbyLabel(type: string): string {
  return type.replace(/_/g, " ");
}

export function configSummary(config: Record<string, unknown>): string {
  const parts = Object.entries(config)
    .slice(0, 4)
    .map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`);
  return parts.join(" · ") || "Default thresholds";
}
