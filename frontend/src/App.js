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
  Button,
  CircularProgress,
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
  const [snippets, setSnippets] = useState([]);
  const [noMoreDiffs, setNoMoreDiffs] = useState(false);

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

  const handleChange = (uuid, content) => {
    setMotifs(motifs.map(motif => (motif.uuid === uuid ? { ...motif, content } : motif)));
  };

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
    if (newValue === 2) {
      fetchNextDiff();
    }
  };

  const fetchNextDiff = () => {
    fetch('http://127.0.0.1:5000/diff-snippets')
      .then(response => {
        if (response.status === 404) {
          setNoMoreDiffs(true);
          return [];
        }
        return response.json();
      })
      .then(data => {
        setSnippets(data);
      })
      .catch(error => {
        console.error('Error fetching snippets:', error);
      });
  };

  const handleValidateSnippets = () => {
    fetch('http://127.0.0.1:5000/validate-snippets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ snippets }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Snippets validated and saved:', data);
        setSnippets([]);
        fetchNextDiff();
      })
      .catch(error => {
        console.error('Error validating snippets:', error);
      });
  };

  const handleSnippetChange = (index, content) => {
    const updatedSnippets = [...snippets];
    updatedSnippets[index] = content;
    setSnippets(updatedSnippets);
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
        <Tab label="Validate Snippets" />
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Content</TableCell>
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
                      onChange={e => handleChange(motif.uuid, e.target.value)}
                    />
                  </TableCell>
                  <TableCell>
                    <Button variant="contained" color="primary" onClick={() => handleSave(motif.uuid, motif.content)}>
                      Save
                    </Button>
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
      <TabPanel value={tabValue} index={2}>
        {noMoreDiffs ? (
          <div>No more diffs to process.</div>
        ) : (
          <>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Snippet</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {snippets.map((snippet, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <TextField
                          fullWidth
                          multiline
                          minRows={3}
                          value={snippet}
                          onChange={e => handleSnippetChange(index, e.target.value)}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Button variant="contained" color="primary" onClick={handleValidateSnippets}>
              Save Validated Snippets
            </Button>
          </>
        )}
      </TabPanel>
    </Container>
  );
}

export default App;