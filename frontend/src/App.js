import React from "react";
import { Container } from "@mui/material";
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
  const tabs = [
    { label: "Reprisals", content: <ReprisalsTab /> },
    { label: "Motifs", content: <MotifsTab /> },
    { label: "Citations", content: <CitationsTab /> },
  ];

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container>
        <h1>Reprise</h1>
        <TabsContainer tabs={tabs} />
      </Container>
    </ThemeProvider>
  );
}

export default App;
