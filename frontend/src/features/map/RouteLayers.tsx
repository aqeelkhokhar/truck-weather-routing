import { CircleMarker, Polyline, Tooltip } from "react-leaflet";
import type { Route } from "../../api/types";
import { formatDateTime, formatDuration, formatMiles } from "../../lib/format";
import { RISK_COLORS, RISK_LABELS } from "../../lib/risk";
import { routeColor, routeLabel } from "../trip/routeLabel";

interface RouteLayersProps {
  route: Route;
  index: number;
  selected: boolean;
  onSelect: () => void;
}

export function RouteLayers({ route, index, selected, onSelect }: RouteLayersProps) {
  const { summary } = route;

  return (
    <>
      <Polyline
        positions={route.geometry}
        eventHandlers={{ click: onSelect }}
        pathOptions={{
          color: routeColor(index),
          weight: selected ? 7 : 4,
          opacity: selected ? 0.9 : 0.5,
          dashArray: selected ? undefined : "8 8",
        }}
      >
        <Tooltip sticky>
          {routeLabel(route.id)}: {formatDuration(summary.duration_seconds)},{" "}
          {formatMiles(summary.distance_miles)}
        </Tooltip>
      </Polyline>
      {route.checkpoints.map((checkpoint) => (
        <CircleMarker
          key={checkpoint.index}
          center={[checkpoint.lat, checkpoint.lon]}
          radius={selected ? 7 : 4}
          eventHandlers={{ click: onSelect }}
          pathOptions={{
            color: "#ffffff",
            weight: selected ? 2 : 1,
            fillColor: RISK_COLORS[checkpoint.level],
            fillOpacity: selected ? 1 : 0.7,
          }}
        >
          <Tooltip>
            <strong>
              {routeLabel(route.id)}, mile {Math.round(checkpoint.mile)}
            </strong>
            <br />
            {RISK_LABELS[checkpoint.level]} risk, ETA {formatDateTime(checkpoint.eta)}
            <br />
            Wind {checkpoint.weather.wind_mph} mph, rain {checkpoint.weather.rain_in_per_hr} in/hr,
            snow {checkpoint.weather.snow_in_per_hr} in/hr
          </Tooltip>
        </CircleMarker>
      ))}
    </>
  );
}
