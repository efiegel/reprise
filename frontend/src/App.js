import React, { useEffect, useState } from 'react';
import {
  Container,
  Tabs,
  Tab,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  CircularProgress,
  Button,
} from '@mui/material';
import './App.css';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={3}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [motifs, setMotifs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [newMotifContent, setNewMotifContent] = useState('');
  const [editingMotif, setEditingMotif] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/motifs')
      .then(response => response.json())
      .then(data => {
        setMotifs(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching motifs:', error);
        setIsLoading(false);
      });
  }, []);

  const handleSave = (uuid, content) => {
    fetch(`http://127.0.0.1:5000/motifs/${uuid}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Motif updated:', data);
        setEditingMotif(null);
      })
      .catch(error => {
        console.error('Error updating motif:', error);
      });
  };

  const handleAddMotif = () => {
    fetch('http://127.0.0.1:5000/motifs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: newMotifContent }),
    })
      .then(response => response.json())
      .then(data => {
        setMotifs([...motifs, data]);
        setNewMotifContent('');
      })
      .catch(error => {
        console.error('Error adding motif:', error);
      });
  };

  const handleDelete = (uuid) => {
    fetch(`http://127.0.0.1:5000/motifs/${uuid}`, {
      method: 'DELETE',
    })
      .then(response => response.json())
      .then(data => {
        console.log('Motif deleted:', data);
        setMotifs(motifs.filter(motif => motif.uuid !== uuid));
      })
      .catch(error => {
        console.error('Error deleting motif:', error);
      });
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleMotifChange = (uuid, content) => {
    setMotifs(motifs.map(motif => (motif.uuid === uuid ? { ...motif, content } : motif)));
    setEditingMotif(uuid);
  };

  if (isLoading) {
    return <CircularProgress />;
  }

  return (
    <Container>
      <h1>Reprise</h1>
      <Tabs value={tabValue} onChange={handleTabChange} aria-label="simple tabs example">
        <Tab label="Motifs" />
        <Tab label="Add Motif" />
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Content</TableCell>
                <TableCell>Created At</TableCell>
                <TableCell>Citation</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {motifs.map(motif => (
                <TableRow key={motif.uuid}>
                  <TableCell>
                    <TextField
                      fullWidth
                      multiline
                      minRows={3}
                      value={motif.content}
                      onChange={e => handleMotifChange(motif.uuid, e.target.value)}
                      onBlur={() => handleSave(motif.uuid, motif.content)}
                      className={editingMotif === motif.uuid ? 'editing' : ''}
                    />
                  </TableCell>
                  <TableCell>{new Date(motif.created_at).toLocaleString()}</TableCell>
                  <TableCell>{motif.citation}</TableCell>
                  <TableCell>
                    <Button variant="contained" color="secondary" onClick={() => handleDelete(motif.uuid)}>
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <TextField
          fullWidth
          multiline
          minRows={3}
          label="New Motif Content"
          value={newMotifContent}
          onChange={e => setNewMotifContent(e.target.value)}
        />
        <Button variant="contained" color="primary" onClick={handleAddMotif}>
          Add Motif
        </Button>
      </TabPanel>
    </Container>
  );
}

export default App;