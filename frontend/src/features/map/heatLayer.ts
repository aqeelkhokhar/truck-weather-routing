import L from "leaflet";

type HeatModule = typeof import("leaflet.heat");

declare global {
  interface Window {
    L: typeof L;
  }
}

let loading: Promise<HeatModule> | null = null;

export function loadHeatPlugin(): Promise<HeatModule> {
  window.L = L;
  loading ??= import("leaflet.heat");
  return loading;
}
