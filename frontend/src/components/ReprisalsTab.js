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
  const [reprisals, setReprisals] = useState([]);
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
        setReprisals(data);
        setRepriseLoading(false);
      })
      .catch(error => {
        console.error('Error fetching reprisals:', error);
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
        <TableContainer component={Paper} sx={{ mt: 2 }}> {/* Add margin-top to the table */}
          <Table>
            <TableBody>
              {reprisals.map(reprisal => (
                <TableRow key={reprisal.uuid}>
                  <TableCell>{reprisal.content}</TableCell>
                  <TableCell>{reprisal.citation}</TableCell>
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
        sx={{ mt: 3 }}
      >
        {repriseLoading ? <CircularProgress size={24} /> : 'Generate'}
      </Button>
    </Box>
  );
}
