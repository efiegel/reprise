import React, { useState, useEffect } from 'react';
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

  const fetchReprisedMotifs = () => {
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

  useEffect(() => {
    // Automatically fetch a new set of reprised motifs on mount
    fetchReprisedMotifs();
  }, []);

  return (
    <Box>
      {reprisedMotifs.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Content</TableCell>
                <TableCell>Citation</TableCell>
                <TableCell>Created At</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reprisedMotifs.map(motif => (
                <TableRow key={motif.uuid}>
                  <TableCell>{motif.content}</TableCell>
                  <TableCell>{motif.citation}</TableCell>
                  <TableCell>{new Date(motif.created_at).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
        <Button
        variant="contained"
        color="primary"
        onClick={fetchReprisedMotifs}
        disabled={repriseLoading}
        sx={{ mb: 2 }}
      >
        {repriseLoading ? <CircularProgress size={24} /> : 'Generate New Reprised Motifs'}
      </Button>
    </Box>
  );
}
