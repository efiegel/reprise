import React, { useState, useEffect } from "react";
import {
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
} from "@mui/material";

export default function CitationsTab() {
  const [citations, setCitations] = useState([]);
  const [newCitationTitle, setNewCitationTitle] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/citations")
      .then((response) => response.json())
      .then((data) => {
        setCitations(data || []);
      })
      .catch((error) => {
        console.error("Error fetching citations:", error);
        setCitations([]);
      });
  }, []);

  const handleAddCitation = () => {
    fetch("http://127.0.0.1:5000/citations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title: newCitationTitle }),
    })
      .then((response) => response.json())
      .then((data) => {
        setNewCitationTitle("");
        setCitations([...citations, data]);
      })
      .catch((error) => {
        console.error("Error adding citation:", error);
      });
  };

  return (
    <Box>
      <Box mb={3}>
        <TextField
          fullWidth
          label="New Citation Title"
          value={newCitationTitle}
          onChange={(e) => setNewCitationTitle(e.target.value)}
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
            {citations.map((citation) => (
              <TableRow key={citation.uuid}>
                <TableCell>{citation.title}</TableCell>
                <TableCell>
                  {new Date(citation.created_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
