import Box from "@mui/material/Box";
import { useState } from "react";
import { CircleMarker, MapContainer, TileLayer, Tooltip } from "react-leaflet";
import type { TripPlan } from "../../api/types";
import { FitBounds } from "./FitBounds";
import { ForecastSlider } from "./ForecastSlider";
import { HeatmapLayer } from "./HeatmapLayer";
import { RiskLegend } from "./RiskLegend";
import { RouteLayers } from "./RouteLayers";

const DEFAULT_CENTER: [number, number] = [39.5, -98.35];
const DEFAULT_ZOOM = 4;
const TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const TILE_ATTRIBUTION = "&copy; OpenStreetMap contributors";

interface TripMapProps {
  plan: TripPlan | null;
  selectedId: string;
  onSelect: (routeId: string) => void;
}

export function TripMap({ plan, selectedId, onSelect }: TripMapProps) {
  const [hour, setHour] = useState(0);
  const [heatmapVisible, setHeatmapVisible] = useState(true);

  return (
    <Box sx={{ position: "relative", height: "100%", minHeight: 420 }}>
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        preferCanvas
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />
        {plan && (
          <>
            <FitBounds plan={plan} />
            {heatmapVisible && <HeatmapLayer heatmap={plan.heatmap} hour={hour} />}
            {plan.routes.map((route, index) => (
              <RouteLayers
                key={route.id}
                route={route}
                index={index}
                selected={route.id === selectedId}
                onSelect={() => onSelect(route.id)}
              />
            ))}
            {[plan.origin, plan.destination].map((place, position) => (
              <CircleMarker
                key={position}
                center={[place.lat, place.lon]}
                radius={9}
                pathOptions={{
                  color: "#ffffff",
                  weight: 3,
                  fillColor: position === 0 ? "#0b3c49" : "#212121",
                  fillOpacity: 1,
                }}
              >
                <Tooltip permanent direction="top">
                  {position === 0 ? "Origin" : "Destination"}
                </Tooltip>
              </CircleMarker>
            ))}
          </>
        )}
      </MapContainer>
      {plan && (
        <>
          <Box sx={{ position: "absolute", top: 12, right: 12, zIndex: 1000 }}>
            <RiskLegend />
          </Box>
          <Box
            sx={{
              position: "absolute",
              left: 12,
              right: 12,
              bottom: 24,
              zIndex: 1000,
              display: "flex",
              justifyContent: "center",
              maxWidth: 560,
              mx: "auto",
            }}
          >
            <ForecastSlider
              baseTime={plan.heatmap.base_time}
              hours={plan.heatmap.hours}
              hour={hour}
              heatmapVisible={heatmapVisible}
              onHourChange={setHour}
              onVisibleChange={setHeatmapVisible}
            />
          </Box>
        </>
      )}
    </Box>
  );
}
