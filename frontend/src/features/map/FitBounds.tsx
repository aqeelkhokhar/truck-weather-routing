import L from "leaflet";
import { useEffect } from "react";
import { useMap } from "react-leaflet";
import type { TripPlan } from "../../api/types";

const BOUNDS_PADDING = 40;

export function FitBounds({ plan }: { plan: TripPlan }) {
  const map = useMap();

  useEffect(() => {
    const points = plan.routes.flatMap((route) => route.geometry);
    if (points.length) {
      map.fitBounds(L.latLngBounds(points), { padding: [BOUNDS_PADDING, BOUNDS_PADDING] });
    }
  }, [map, plan]);

  return null;
}
