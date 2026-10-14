import Chip from "@mui/material/Chip";
import type { RiskLevel } from "../../api/types";
import { RISK_COLORS, RISK_LABELS } from "../../lib/risk";

export function RiskChip({ level }: { level: RiskLevel }) {
  return (
    <Chip
      size="small"
      label={RISK_LABELS[level]}
      sx={{ bgcolor: RISK_COLORS[level], color: "#fff", fontWeight: 600, minWidth: 76 }}
    />
  );
}
