import React from 'react';
import { Container } from '@mui/material';
import TabsContainer from './components/TabsContainer';
import MotifsTab from './components/MotifsTab';
import CitationsTab from './components/CitationsTab';
import ReprisedMotifsTab from './components/ReprisedMotifsTab';

function App() {
  const tabs = [
    { label: 'Motifs', content: <MotifsTab /> },
    { label: 'Citations', content: <CitationsTab /> },
    { label: 'Reprised Motifs', content: <ReprisedMotifsTab /> },
  ];

  return (
    <Container>
      <h1>Reprise</h1>
      <TabsContainer tabs={tabs} />
    </Container>
  );
}

export default App;