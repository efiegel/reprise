import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
} from '@mui/material';

export default function ReprisedMotifsTab() {
  const [reprisedMotifs, setReprisedMotifs] = useState([]);
  const [repriseLoading, setRepriseLoading] = useState(false);

  const handleReprise = () => {
    setRepriseLoading(true);
    fetch('http://127.0.0.1:5000/reprise', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        setReprisedMotifs(data);
        setRepriseLoading(false);
      })
      .catch(error => {
        console.error('Error fetching reprised motifs:', error);
        setRepriseLoading(false);
      });
  };

  return (
    <Box>
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
    </Box>
  );
}
