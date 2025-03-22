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

export default function ReprisalsTab() {
  const [reprisals, setReprisals] = useState([]); // Updated variable name
  const [repriseLoading, setRepriseLoading] = useState(false);

  const fetchReprisals = () => {
    setRepriseLoading(true);
    fetch('http://127.0.0.1:5000/reprise', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        setReprisals(data); // Updated variable name
        setRepriseLoading(false);
      })
      .catch(error => {
        console.error('Error fetching reprisals:', error); // Updated label
        setRepriseLoading(false);
      });
  };

  useEffect(() => {
    // Automatically fetch a new set of reprisals on mount
    fetchReprisals();
  }, []);

  return (
    <Box>
      {reprisals.length > 0 && (
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
              {reprisals.map(reprisal => (
                <TableRow key={reprisal.uuid}>
                  <TableCell>{reprisal.content}</TableCell>
                  <TableCell>{reprisal.citation}</TableCell>
                  <TableCell>{new Date(reprisal.created_at).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      <Button
        variant="contained"
        color="primary"
        onClick={fetchReprisals}
        disabled={repriseLoading}
        sx={{ mb: 2 }}
      >
        {repriseLoading ? <CircularProgress size={24} /> : 'Generate New Reprisals'} {/* Updated label */}
      </Button>
    </Box>
  );
}
