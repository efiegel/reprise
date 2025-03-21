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
  MenuItem,
  Select,
  InputLabel,
  FormControl,
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
  const [citations, setCitations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [newMotifContent, setNewMotifContent] = useState('');
  const [selectedCitation, setSelectedCitation] = useState('');
  const [newCitationTitle, setNewCitationTitle] = useState('');
  const [editingMotif, setEditingMotif] = useState(null);
  const [reprisedMotifs, setReprisedMotifs] = useState([]);
  const [repriseLoading, setRepriseLoading] = useState(false);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/motifs')
      .then(response => response.json())
      .then(data => {
        const sortedMotifs = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setMotifs(sortedMotifs);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching motifs:', error);
        setIsLoading(false);
      });

    fetch('http://127.0.0.1:5000/citations')
      .then(response => response.json())
      .then(data => {
        setCitations(data);
      })
      .catch(error => {
        console.error('Error fetching citations:', error);
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
      body: JSON.stringify({ content: newMotifContent, citation: selectedCitation }),
    })
      .then(response => response.json())
      .then(data => {
        const updatedMotifs = [data, ...motifs];
        setMotifs(updatedMotifs);
        setNewMotifContent('');
      })
      .catch(error => {
        console.error('Error adding motif:', error);
      });
  };

  const handleAddCitation = () => {
    fetch('http://127.0.0.1:5000/citations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title: newCitationTitle }),
    })
      .then(response => response.json())
      .then(data => {
        setNewCitationTitle('');
        setCitations([...citations, data]);
      })
      .catch(error => {
        console.error('Error adding citation:', error);
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

  const handleReprise = () => {
    setRepriseLoading(true);
    fetch('http://127.0.0.1:5000/reprise',{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    }
    )
      .then(response => response.json())
      .then(data => {
        const sortedMotifs = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setReprisedMotifs(sortedMotifs);
        setRepriseLoading(false);
      })
      .catch(error => {
        console.error('Error fetching reprised motifs:', error);
        setRepriseLoading(false);
      });
  };

  if (isLoading) {
    return <CircularProgress />;
  }

  return (
    <Container>
      <h1>Reprise</h1>
      <Tabs value={tabValue} onChange={handleTabChange} aria-label="simple tabs example">
        <Tab label="Motifs" />
        <Tab label="Citations" />
        <Tab label="Reprised Motifs" />
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        <Box mb={3}>
          <TextField
            fullWidth
            multiline
            minRows={3}
            label="New Motif Content"
            value={newMotifContent}
            onChange={e => setNewMotifContent(e.target.value)}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="citation-select-label">Citation</InputLabel>
            <Select
              labelId="citation-select-label"
              value={selectedCitation}
              onChange={e => setSelectedCitation(e.target.value)}
              displayEmpty
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {citations.map(citation => (
                <MenuItem key={citation.uuid} value={citation.title}>
                  {citation.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" color="primary" onClick={handleAddMotif}>
            Add Motif
          </Button>
        </Box>
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
        <Box mb={3}>
          <TextField
            fullWidth
            label="New Citation Title"
            value={newCitationTitle}
            onChange={e => setNewCitationTitle(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="primary" onClick={handleAddCitation}>
            Add Citation
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Created At</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {citations.map(citation => (
                <TableRow key={citation.uuid}>
                  <TableCell>{citation.title}</TableCell>
                  <TableCell>{new Date(citation.created_at).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleReprise}
          disabled={repriseLoading}
          sx={{ mb: 2 }}
        >
          {repriseLoading ? <CircularProgress size={24} /> : 'Generate Reprised Motifs'}
        </Button>
        
        {reprisedMotifs.length > 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Content</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell>Citation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reprisedMotifs.map(motif => (
                  <TableRow key={motif.uuid}>
                    <TableCell>{motif.content}</TableCell>
                    <TableCell>{new Date(motif.created_at).toLocaleString()}</TableCell>
                    <TableCell>{motif.citation}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>
    </Container>
  );
}

export default App;