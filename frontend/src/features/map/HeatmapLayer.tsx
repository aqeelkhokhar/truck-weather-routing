import L from "leaflet";
import { useEffect, useMemo, useState } from "react";
import { useMap } from "react-leaflet";
import type { Heatmap } from "../../api/types";
import { HEAT_GRADIENT } from "../../lib/risk";
import { loadHeatPlugin } from "./heatLayer";

const MAX_LEVEL = 4;
const HEAT_RADIUS = 28;
const HEAT_BLUR = 22;

interface HeatmapLayerProps {
  heatmap: Heatmap;
  hour: number;
}

export function HeatmapLayer({ heatmap, hour }: HeatmapLayerProps) {
  const map = useMap();
  const [layer, setLayer] = useState<L.HeatLayer | null>(null);

  const frames = useMemo(
    () =>
      Array.from({ length: heatmap.hours + 1 }, (_, step) =>
        heatmap.points
          .map((point): [number, number, number] => [
            point.lat,
            point.lon,
            (point.levels[step] ?? 0) / MAX_LEVEL,
          ])
          .filter(([, , intensity]) => intensity > 0),
      ),
    [heatmap],
  );

  useEffect(() => {
    let cancelled = false;
    let created: L.HeatLayer | null = null;
    void loadHeatPlugin().then(() => {
      if (cancelled) return;
      created = L.heatLayer([], {
        radius: HEAT_RADIUS,
        blur: HEAT_BLUR,
        max: 1,
        minOpacity: 0.35,
        gradient: HEAT_GRADIENT,
      }).addTo(map);
      setLayer(created);
    });
    return () => {
      cancelled = true;
      created?.remove();
      setLayer(null);
    };
  }, [map]);

  useEffect(() => {
    layer?.setLatLngs(frames[Math.min(hour, frames.length - 1)] ?? []);
  }, [layer, frames, hour]);

  return null;
}
