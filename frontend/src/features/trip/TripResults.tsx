import Stack from "@mui/material/Stack";
import type { TripPlan } from "../../api/types";
import { CheckpointTable } from "./CheckpointTable";
import { RecommendationBanner } from "./RecommendationBanner";
import { RouteCard } from "./RouteCard";

interface TripResultsProps {
  plan: TripPlan;
  selectedId: string;
  onSelect: (routeId: string) => void;
}

export function TripResults({ plan, selectedId, onSelect }: TripResultsProps) {
  const selected = plan.routes.find((route) => route.id === selectedId) ?? plan.routes[0];

  return (
    <Stack spacing={2}>
      <RecommendationBanner recommendation={plan.recommendation} />
      {plan.routes.map((route, index) => (
        <RouteCard
          key={route.id}
          route={route}
          index={index}
          selected={route.id === selected?.id}
          onSelect={() => onSelect(route.id)}
        />
      ))}
      {selected && <CheckpointTable route={selected} />}
    </Stack>
  );
}
