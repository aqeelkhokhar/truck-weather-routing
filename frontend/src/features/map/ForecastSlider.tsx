import Box from "@mui/material/Box";
import FormControlLabel from "@mui/material/FormControlLabel";
import Paper from "@mui/material/Paper";
import Slider from "@mui/material/Slider";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { addHours, formatDateTime } from "../../lib/format";

const SLIDER_MARKS = [0, 12, 24, 36, 48].map((value) => ({ value, label: `+${value}h` }));

interface ForecastSliderProps {
  baseTime: string;
  hours: number;
  hour: number;
  heatmapVisible: boolean;
  onHourChange: (hour: number) => void;
  onVisibleChange: (visible: boolean) => void;
}

export function ForecastSlider(props: ForecastSliderProps) {
  const { baseTime, hours, hour, heatmapVisible, onHourChange, onVisibleChange } = props;

  return (
    <Paper elevation={3} sx={{ px: 2.5, pt: 1.25, pb: 1, width: "100%" }}>
      <Stack
        direction="row"
        sx={{ justifyContent: "space-between", alignItems: "center", flexWrap: "wrap" }}
      >
        <Box>
          <Typography variant="caption" sx={{ fontWeight: 700, display: "block" }}>
            Weather heatmap forecast
          </Typography>
          <Typography variant="body2">
            {hour === 0 ? "Now" : `In ${hour}h`}, {formatDateTime(addHours(baseTime, hour))}
          </Typography>
        </Box>
        <FormControlLabel
          label="Heatmap"
          control={
            <Switch
              size="small"
              checked={heatmapVisible}
              onChange={(_, checked) => onVisibleChange(checked)}
            />
          }
        />
      </Stack>
      <Slider
        value={hour}
        min={0}
        max={hours}
        step={1}
        marks={SLIDER_MARKS}
        disabled={!heatmapVisible}
        valueLabelDisplay="auto"
        valueLabelFormat={(value) => `+${value}h`}
        onChange={(_, value) => onHourChange(value)}
        aria-label="Forecast hour"
      />
    </Paper>
  );
}
