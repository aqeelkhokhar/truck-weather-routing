import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import type { Recommendation } from "../../api/types";
import { DECISION_REASONS } from "../../lib/risk";
import { routeLabel } from "./routeLabel";

export function RecommendationBanner({ recommendation }: { recommendation: Recommendation }) {
  if (recommendation.all_routes_blocked) {
    return (
      <Alert severity="error" icon={<WarningAmberIcon />}>
        <AlertTitle>No safe route at this departure time</AlertTitle>
        Every route crosses a no travel checkpoint. Try a later departure or a lighter load.
      </Alert>
    );
  }
  return (
    <Alert severity="success" icon={<CheckCircleIcon />}>
      <AlertTitle>Recommended: {routeLabel(recommendation.route_id)}</AlertTitle>
      {DECISION_REASONS[recommendation.decided_by]}
    </Alert>
  );
}
