import React from "react";
import { Container } from "@mui/material";
import TabsContainer from "./components/TabsContainer";
import MotifsTab from "./components/MotifsTab";
import CitationsTab from "./components/CitationsTab";
import ReprisalsTab from "./components/ReprisalsTab";

function App() {
  const tabs = [
    { label: "Reprisals", content: <ReprisalsTab /> },
    { label: "Motifs", content: <MotifsTab /> },
    { label: "Citations", content: <CitationsTab /> },
  ];

  return (
    <Container>
      <h1>Reprise</h1>
      <TabsContainer tabs={tabs} />
    </Container>
  );
}

export default App;
