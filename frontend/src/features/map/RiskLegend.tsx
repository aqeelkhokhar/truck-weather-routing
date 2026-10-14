import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { RISK_COLORS, RISK_LABELS, RISK_ORDER } from "../../lib/risk";

export function RiskLegend() {
  return (
    <Paper elevation={3} sx={{ p: 1.25 }}>
      <Typography variant="caption" sx={{ fontWeight: 700, display: "block", mb: 0.5 }}>
        Checkpoint risk
      </Typography>
      <Stack spacing={0.25}>
        {RISK_ORDER.map((level) => (
          <Stack key={level} direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <Box sx={{ width: 12, height: 12, borderRadius: "50%", bgcolor: RISK_COLORS[level] }} />
            <Typography variant="caption">{RISK_LABELS[level]}</Typography>
          </Stack>
        ))}
      </Stack>
    </Paper>
  );
}
