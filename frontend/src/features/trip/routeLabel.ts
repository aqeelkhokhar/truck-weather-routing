export function routeLabel(routeId: string): string {
  return `Route ${routeId.replace("route-", "")}`;
}

export const ROUTE_COLORS = ["#1565c0", "#6a1b9a", "#00838f"];

export function routeColor(index: number): string {
  return ROUTE_COLORS[index % ROUTE_COLORS.length] ?? "#1565c0";
}
