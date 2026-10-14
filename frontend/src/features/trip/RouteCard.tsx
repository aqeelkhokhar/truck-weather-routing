import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { Route } from "../../api/types";
import { formatDateTime, formatDuration, formatMiles } from "../../lib/format";
import { riskFromIndex } from "../../lib/risk";
import { RiskChip } from "./RiskChip";
import { routeColor, routeLabel } from "./routeLabel";

interface RouteCardProps {
  route: Route;
  index: number;
  selected: boolean;
  onSelect: () => void;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ minWidth: 0 }}>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
        {label}
      </Typography>
      <Typography variant="body2" noWrap sx={{ fontWeight: 600 }}>
        {value}
      </Typography>
    </Box>
  );
}

export function RouteCard({ route, index, selected, onSelect }: RouteCardProps) {
  const { summary } = route;
  const arrival = route.checkpoints[route.checkpoints.length - 1]?.eta;
  const overall = summary.blocked ? "NO_TRAVEL" : riskFromIndex(summary.average_risk);

  return (
    <Card
      variant="outlined"
      sx={{
        borderColor: selected ? routeColor(index) : "divider",
        borderWidth: selected ? 2 : 1,
        borderLeftWidth: 6,
        borderLeftColor: routeColor(index),
      }}
    >
      <CardActionArea onClick={onSelect} aria-pressed={selected}>
        <CardContent>
          <Stack
            direction="row"
            sx={{ alignItems: "center", justifyContent: "space-between", mb: 1.5 }}
          >
            <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
              <Typography variant="h2">{routeLabel(route.id)}</Typography>
              {route.recommended && <Chip size="small" color="success" label="Recommended" />}
            </Stack>
            <RiskChip level={overall} />
          </Stack>
          <Box sx={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 1.5 }}>
            <Metric label="Travel time" value={formatDuration(summary.duration_seconds)} />
            <Metric label="Distance" value={formatMiles(summary.distance_miles)} />
            <Metric label="Arrival" value={arrival ? formatDateTime(arrival) : "-"} />
            <Metric label="Severe miles" value={formatMiles(summary.severe_miles)} />
            <Metric label="High miles" value={formatMiles(summary.high_miles)} />
            <Metric label="Average risk" value={`${summary.average_risk.toFixed(2)} of 4`} />
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
