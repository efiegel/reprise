import React, { useEffect, useState } from 'react';
import {
  Container,
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

function App() {
  const [motifs, setMotifs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

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

  if (isLoading) {
    return <CircularProgress />;
  }

  return (
    <Container>
      <h1>Reprise</h1>
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
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default App;