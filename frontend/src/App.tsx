import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { TripMap } from "./features/map/TripMap";
import { TripForm } from "./features/trip/TripForm";
import { TripResults } from "./features/trip/TripResults";
import { useTripPlan } from "./features/trip/useTripPlan";
import type { TripRequest } from "./api/types";

const PANEL_WIDTH = 440;
const STACKED_MAP_HEIGHT = 480;

export default function App() {
  const { plan, loading, errors, submit } = useTripPlan();
  const [selectedId, setSelectedId] = useState("");

  async function handleSubmit(request: TripRequest) {
    setSelectedId("");
    await submit(request);
  }

  const activeId = selectedId || plan?.recommendation.route_id || "";

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        height: { md: "100vh" },
        minHeight: "100vh",
      }}
    >
      <Box
        component="aside"
        sx={{
          width: { xs: "100%", md: PANEL_WIDTH },
          flexShrink: 0,
          overflowY: "auto",
          p: 2.5,
          bgcolor: "background.default",
          borderRight: { md: 1 },
          borderColor: "divider",
        }}
      >
        <Stack spacing={3}>
          <Stack direction="row" spacing={1.25} sx={{ alignItems: "center" }}>
            <LocalShippingIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="h1" component="h1">
                Weather aware truck routing
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pick the safest route by weather, load and travel time.
              </Typography>
            </Box>
          </Stack>
          <TripForm loading={loading} errors={errors} onSubmit={handleSubmit} />
          {plan && <TripResults plan={plan} selectedId={activeId} onSelect={setSelectedId} />}
        </Stack>
      </Box>
      <Box
        component="main"
        sx={{
          flex: { xs: "none", md: 1 },
          height: { xs: STACKED_MAP_HEIGHT, md: "auto" },
          minHeight: { md: 0 },
        }}
      >
        <TripMap plan={plan} selectedId={activeId} onSelect={setSelectedId} />
      </Box>
    </Box>
  );
}
