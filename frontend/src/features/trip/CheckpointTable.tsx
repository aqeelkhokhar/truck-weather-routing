import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import type { Route } from "../../api/types";
import { formatDateTime } from "../../lib/format";
import { RiskChip } from "./RiskChip";
import { routeLabel } from "./routeLabel";

export function CheckpointTable({ route }: { route: Route }) {
  return (
    <Paper variant="outlined">
      <Typography variant="h2" sx={{ p: 1.5, pb: 0.5 }}>
        {routeLabel(route.id)} checkpoints
      </Typography>
      <TableContainer sx={{ maxHeight: 320 }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Mile</TableCell>
              <TableCell>ETA</TableCell>
              <TableCell align="right">Wind</TableCell>
              <TableCell align="right">Rain</TableCell>
              <TableCell align="right">Snow</TableCell>
              <TableCell>Risk</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {route.checkpoints.map((checkpoint) => (
              <TableRow key={checkpoint.index} hover>
                <TableCell>{Math.round(checkpoint.mile)}</TableCell>
                <TableCell>{formatDateTime(checkpoint.eta)}</TableCell>
                <TableCell align="right">{checkpoint.weather.wind_mph} mph</TableCell>
                <TableCell align="right">{checkpoint.weather.rain_in_per_hr} in/hr</TableCell>
                <TableCell align="right">{checkpoint.weather.snow_in_per_hr} in/hr</TableCell>
                <TableCell>
                  <RiskChip level={checkpoint.level} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
