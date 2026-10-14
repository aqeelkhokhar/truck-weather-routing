export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "SEVERE" | "NO_TRAVEL";

export type DecidedBy =
  | "no_travel"
  | "severe_miles"
  | "high_miles"
  | "average_risk"
  | "travel_time"
  | "tie"
  | "only_route";

export interface TripRequest {
  origin: string;
  destination: string;
  departure: string;
  load_lb: number;
  spacing_miles: number;
}

export interface Location {
  name: string;
  lat: number;
  lon: number;
}

export interface Weather {
  wind_mph: number;
  rain_in_per_hr: number;
  snow_in_per_hr: number;
}

export interface Checkpoint {
  index: number;
  mile: number;
  lat: number;
  lon: number;
  eta: string;
  level: RiskLevel;
  weather: Weather;
}

export interface RouteSummary {
  distance_miles: number;
  duration_seconds: number;
  severe_miles: number;
  high_miles: number;
  no_travel_miles: number;
  average_risk: number;
  blocked: boolean;
}

export interface Route {
  id: string;
  recommended: boolean;
  geometry: [number, number][];
  summary: RouteSummary;
  checkpoints: Checkpoint[];
}

export interface Recommendation {
  route_id: string;
  decided_by: DecidedBy;
  all_routes_blocked: boolean;
}

export interface HeatmapPoint {
  lat: number;
  lon: number;
  levels: number[];
}

export interface Heatmap {
  base_time: string;
  hours: number;
  points: HeatmapPoint[];
}

export interface TripPlan {
  origin: Location;
  destination: Location;
  recommendation: Recommendation;
  routes: Route[];
  heatmap: Heatmap;
}
