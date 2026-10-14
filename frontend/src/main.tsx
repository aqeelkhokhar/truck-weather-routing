import CssBaseline from "@mui/material/CssBaseline";
import GlobalStyles from "@mui/material/GlobalStyles";
import { ThemeProvider } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "leaflet/dist/leaflet.css";
import App from "./App";
import { theme } from "./theme";

const mapStyles = { ".leaflet-heatmap-layer": { pointerEvents: "none" } };

const container = document.getElementById("root");

if (container) {
  createRoot(container).render(
    <StrictMode>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles styles={mapStyles} />
        <App />
      </ThemeProvider>
    </StrictMode>,
  );
}
