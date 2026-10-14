import SearchIcon from "@mui/icons-material/Search";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import InputAdornment from "@mui/material/InputAdornment";
import Stack from "@mui/material/Stack";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState, type FormEvent } from "react";
import type { TripRequest } from "../../api/types";
import { toLocalInputValue } from "../../lib/format";

const SPACING_OPTIONS = [10, 25, 50];
const DEFAULT_LOAD_LB = 30000;
const MAX_LOAD_LB = 120000;
const DEFAULT_LEAD_MS = 60 * 60 * 1000;

interface TripFormProps {
  loading: boolean;
  errors: string[];
  onSubmit: (request: TripRequest) => void;
}

export function TripForm({ loading, errors, onSubmit }: TripFormProps) {
  const [origin, setOrigin] = useState("Chicago, IL");
  const [destination, setDestination] = useState("Dallas, TX");
  const [departure, setDeparture] = useState(() =>
    toLocalInputValue(new Date(Date.now() + DEFAULT_LEAD_MS)),
  );
  const [load, setLoad] = useState(String(DEFAULT_LOAD_LB));
  const [spacing, setSpacing] = useState(25);

  const loadValue = Number(load);
  const loadInvalid =
    load === "" || !Number.isFinite(loadValue) || loadValue < 0 || loadValue > MAX_LOAD_LB;
  const canSubmit = !loading && origin.trim() && destination.trim() && departure && !loadInvalid;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmit({
      origin: origin.trim(),
      destination: destination.trim(),
      departure: new Date(departure).toISOString(),
      load_lb: Math.round(loadValue),
      spacing_miles: spacing,
    });
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <Stack spacing={2}>
        <TextField
          label="Origin"
          value={origin}
          onChange={(event) => setOrigin(event.target.value)}
          size="small"
          required
          fullWidth
        />
        <TextField
          label="Destination"
          value={destination}
          onChange={(event) => setDestination(event.target.value)}
          size="small"
          required
          fullWidth
        />
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <TextField
            label="Departure"
            type="datetime-local"
            value={departure}
            onChange={(event) => setDeparture(event.target.value)}
            size="small"
            required
            fullWidth
            slotProps={{ inputLabel: { shrink: true } }}
          />
          <TextField
            label="Load weight"
            type="number"
            value={load}
            onChange={(event) => setLoad(event.target.value)}
            size="small"
            required
            fullWidth
            error={loadInvalid}
            helperText={loadInvalid ? `0 to ${MAX_LOAD_LB.toLocaleString("en-US")} lb` : " "}
            slotProps={{
              input: { endAdornment: <InputAdornment position="end">lb</InputAdornment> },
            }}
          />
        </Stack>
        <Stack spacing={0.75}>
          <Typography variant="caption" color="text.secondary">
            Weather checkpoint spacing
          </Typography>
          <ToggleButtonGroup
            exclusive
            fullWidth
            size="small"
            color="primary"
            value={spacing}
            onChange={(_, value: number | null) => value && setSpacing(value)}
          >
            {SPACING_OPTIONS.map((miles) => (
              <ToggleButton key={miles} value={miles}>
                Every {miles} mi
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Stack>
        {errors.map((message) => (
          <Alert key={message} severity="error">
            {message}
          </Alert>
        ))}
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={!canSubmit}
          startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <SearchIcon />}
        >
          {loading ? "Checking weather along 3 routes" : "Find safest route"}
        </Button>
      </Stack>
    </form>
  );
}
