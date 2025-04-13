import React from "react";
import { Container, Link, Box } from "@mui/material";
import TabsContainer from "./components/TabsContainer";
import MotifsTab from "./components/MotifsTab";
import CitationsTab from "./components/CitationsTab";
import ReprisalsTab from "./components/ReprisalsTab";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

function App() {
  const logfireUrl = process.env.REACT_APP_LOGFIRE_PROJECT_URL;
  const tabs = [
    { label: "Reprisals", content: <ReprisalsTab /> },
    { label: "Motifs", content: <MotifsTab /> },
    { label: "Citations", content: <CitationsTab /> },
  ];

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <h1>Reprise</h1>
          {logfireUrl && (
            <Link
              href={logfireUrl}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ fontSize: "0.8rem", color: "text.secondary" }}
            >
              {logfireUrl}
            </Link>
          )}
        </Box>
        <TabsContainer tabs={tabs} />
      </Container>
    </ThemeProvider>
  );
}

export default App;
